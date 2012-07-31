from scipy import optimize
from numpy import array, inf
import pdb

def curve_fit(fct, xdata, ydata, p0, args=(), residuals=None, fix_params=(), *lsq_args, **lsq_kword):
    """
    Fit a curve using the optimize.leastsq function

    Parameters
    ----------
    fct: callable
        Function to optimize. The call will be equivalent to ``fct(xdata, p0, *args)``
    xdata: ndarray
        Explaining values
    ydata: ndarray
        Target values
    p0: tuple
        Initial estimates for the parameters of fct
    args: tuple
        Additional arguments for the function
    residuals: callable or None
        Function computing the residuals. The call is equivalent to ``residuals(y,y)``
        and it should return a ndarray
    fix_params: tuple of int
        List of indices for the parameters in p0 that shouldn't change
    lsq_args: tuple
        List of unnamed arguments passed to ``optimize.leastsq``, starting with ``ftol``
    lsq_kword: dict
        Dictionnary of named arguments passed to ``optional.leastsq`, starting with ``ftol``

    Returns
    -------
    popt: ndarray
        The solution (or the result of the last iteration for an unsuccessful
        call)
    pcov : 2d array
        The estimated covariance of popt.  The diagonals provide the variance
        of the parameter estimate.
    res: ndarray
        Final residuals
    infodict: dict
        a dictionary of outputs with the keys::
            - 'nfev' : the number of function calls
            - 'fvec' : the function evaluated at the output
            - 'fjac' : A permutation of the R matrix of a QR factorization of
                     the final approximate Jacobian matrix, stored column wise.
                     Together with ipvt, the covariance of the estimate can be
                     approximated.
            - 'ipvt' : an integer array of length N which defines a permutation
                     matrix, p, such that fjac*p = q*r, where r is upper
                     triangular with diagonal elements of nonincreasing
                     magnitude. Column j of p is column ipvt(j) of the identity
                     matrix.
            - 'qtf'  : the vector (transpose(q) * fvec).
            - 'CI'   : list of tuple of parameters, each being the lower and
                     upper bounds for the confidence interval in the CI
                     argument at the same position.

    Notes
    -----
    In this implementation, residuals is supposed to be a generalisation of the
    notion of difference. In the end, the mathematical expression of this
    function is:

        min  sum(residuals(f(xdata),ydata)**2, axis=0)
      params

    Confidence interval are estimated using the bootstrap method.
    """
    if residuals is None:
        residuals = lambda x,y: (y-x)

    f = None

    if fix_params:
        p_save = array(p0, dtype=float)
        change_params = range(len(p0))
        try:
            for i in fix_params:
                change_params.remove(i)
        except ValueError:
            raise ValueError("List of parameters to fix is incorrect: contains either duplicates or values out of range.")
        p0 = p_save[change_params]
        def f(p, *args):
            p1 = array(p_save)
            p1[change_params] = p
            y0 = fct(xdata,p1,*args)
            return residuals(y0, ydata)
    else:
        def f(*args):
            y0 = fct(xdata,*args)
            return residuals(y0, ydata)
    popt, pcov, infodict, mesg, ier = optimize.leastsq(f, p0, args, None, 1, 0, *lsq_args, **lsq_kword)

    if fix_params:
        p_save[change_params] = popt
        popt = p_save

    if not ier in [1,2,3,4]:
        raise RuntimeError("Unable to determine number of fit parameters. Error returned by scipy.optimize.leastsq:\n%s" % (mesg,))

    res = residuals(fct(xdata, popt, *args), ydata)
    if (len(res) > len(p0)) and pcov is not None:
        s_sq = (res**2).sum()/(len(ydata)-len(p0))
        pcov = pcov * s_sq
    else:
        pcov = inf

    return popt, pcov, res, infodict
