"""This is meant as a simple interface to CRMod, i.e. the forward operator and
its Jacobian. Nothing more.

It can be used to experiment with alternative inversion strategies outside of
the old FORTRAN code, but bear in mind that the CRMod binary is used to compute
everything. This is slow and involves writing things to disc. If possible use
another, better interfaced forward code such as pygimli.

The plan is to support both resistivity-only and complex (magnitude/phase)
versions.
"""
import os
import numpy as np

import crtomo
from crtomo.grid import crt_grid


class crmod_interface(object):
    def __init__(self, grid, configs, tempdir=None):
        """Initialize the CRMod interface

        Parameters
        ----------
        grid : crtomo.grid.crt_grid
            FE grid to work with
        configs : Nx4 numpy.ndarray
            Measurement configurations to work with (ABMN)
        tempdir : string, optional
            If set, use this directory for (temporary) file output. For example
            using the RAM-disc (/dev/shm) can potentially speed things up a
            lot.
        """
        assert isinstance(configs, np.ndarray)
        assert isinstance(grid, crt_grid)
        if tempdir is not None:
            assert os.path.isdir(tempdir)

        self.grid = grid
        self.configs = configs
        self.tempdir = tempdir

    def _get_tdm(self, m):
        """For a given model of resistivity magnitudes and phases, return a
        tdMan instance

        Parameters
        ----------
        m : Nx1|Nx2 ndarray
            N Model parameters, first column linear magnitudes [ohm m], second
            column phase values [mrad]

        Returns
        -------
        tdm : crtomo.tdMan
            td manager
        """
        if len(m.shape) == 1:
            m = m[:, np.newaxis]
        assert len(m.shape) == 2
        # print('gettm')
        # import IPython
        # IPython.embed()
        tdm = crtomo.tdMan(grid=self.grid, tempdir=self.tempdir)
        tdm.configs.add_to_configs(self.configs)

        pid_mag = tdm.parman.add_data(m[:, 0])
        tdm.register_magnitude_model(pid_mag)
        if m.shape[0] == 2:
            pid_pha = tdm.parman.add_data(m[:, 1])
        else:
            pid_pha = tdm.parman.add_data(np.zeros(m.shape[0]))
        tdm.register_phase_model(pid_pha)
        return tdm

    def forward_complex(self, log_sigma):
        r"""Compute a model response, i.e. complex impedances

        Parameters
        ----------
        log_sigma : 1xN or 2xN numpy.ndarray
            Model parameters. First column: :math:`log_e(\sigma)`, second
            column: :math:`\phi_{cond} [mrad]`.  If first dimension is of
            length one, assume phase values to be zero.

        Returns
        -------
        measurements : Nx2 numpy.ndarray
            Return log_e Y values of computed forward response
        """
        log_sigma = np.atleast_2d(log_sigma)
        rmag = 1.0 / np.exp(log_sigma[0, :])
        if log_sigma.shape[0] == 1:
            rpha = np.zeros_like(rmag)
        else:
            # convert to resistivities
            rpha = -log_sigma[1, :]
        m = np.vstack((rmag, rpha)).T
        tdm = self._get_tdm(m)
        measurements = tdm.measurements()
        # convert R to log Y
        measurements[:, 0] = np.log(1.0 / measurements[:, 0])
        # convert rpha to cpha
        measurements[:, 1] *= -1
        return measurements

    def J(self, log_sigma):
        """Return the sensitivity matrix

        Parameters
        ----------
        log_sigma : numpy.ndarray
            log_e conductivities

        """
        m = 1.0 / np.exp(log_sigma)
        tdm = self._get_tdm(m)

        tdm.model(
            sensitivities=True,
            # output_directory=stage_dir + 'modeling',
        )

        measurements = tdm.measurements()

        # build up the sensitivity matrix
        sens_list = []
        for config_nr, cids in sorted(
                tdm.assignments['sensitivities'].items()):
            sens_list.append(tdm.parman.parsets[cids[0]])

        # [del V / del sigma]
        sensitivities_lin = np.array(sens_list)

        # now convert to the log-sensitivities relevant for CRTomo and the
        # resolution matrix
        sensitivities_log = sensitivities_lin
        # multiply measurements on first dimension
        measurements_rep = np.repeat(
            measurements[:, 0, np.newaxis],
            sensitivities_lin.shape[1],
            axis=1)
        # sensitivities_log = sensitivities_log * mfit

        # multiply resistivities on second dimension
        m_rep = np.repeat(
            m[np.newaxis, :], sensitivities_lin.shape[0], axis=0
        )

        # eq. 3.41 in Kemna, 2000: notice that m_rep here is in rho, not sigma
        factor = - 1 / (m_rep * measurements_rep)
        sensitivities_log = factor * sensitivities_lin

#         import IPython
#         IPython.embed()

        return sensitivities_log

    def fwd_complex_logY_sigma(self, sigma):
        """Compute a model response from linear complex conductivities

        Parameters
        ----------
        sigma : 1xN or 2xN numpy.ndarray
            Model parameters as sigma and sigma phase, N the number of cells.
            If first dimension is of length one, assume phase values to be zero

        Returns
        -------
        measurements : Nx2 numpy nd array
            Return log_e sigma values of computed forward response (i.e., first
            column: log(sigma), second column: sigma phase
        """
        m_rmag = 1.0 / sigma
        tdm = self._get_tdm(m_rmag)
        measurements = tdm.measurements()
        # import IPython
        # IPython.embed()
        # convert R to log Y
        measurements[:, 0] = np.log(1.0 / measurements[:, 0])
        # convert resistivity phase to conductivity phase
        measurements[:, 1] *= -1
        return measurements

    def J_complex_logY_sigma(self, sigma):
        """Return the sensitivity matrix

        At this point works only with resistivities.
        Parameters
        ----------
        sigma : numpy.ndarray
            log_e conductivities

        """
        m_rmag = 1.0 / sigma
        tdm = self._get_tdm(m_rmag)

        tdm.model(
            sensitivities=True,
            # output_directory=stage_dir + 'modeling',
        )

        measurements = tdm.measurements()

        # build up the sensitivity matrix
        sens_list = []
        for config_nr, cids in sorted(
                tdm.assignments['sensitivities'].items()):
            sens_list.append(tdm.parman.parsets[cids[0]])

        # [del V / del sigma]
        sensitivities_lin = np.array(sens_list)

        # multiply measurements on first dimension
        measurements_rep = np.repeat(
            measurements[:, 0, np.newaxis],
            sensitivities_lin.shape[1],
            axis=1)

        # after, eq. 3.41 in Kemna, 2000: notice that m_rep here is in rho, not
        # sigma
        # however, we now have model parameters in linear
        factor = -1 / measurements_rep
        sensitivities_logY = factor * sensitivities_lin

        return sensitivities_logY
