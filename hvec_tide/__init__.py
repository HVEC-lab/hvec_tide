"""
Convenience functions supporting the use of the package
Utide, created by Wesley Bowman.

Created by HVEC, the practical knowledge provider, 2022.

References
Codiga, Daniel. (2011). Unified tidal analysis and 
    prediction using the UTide Matlab functions. 10.13140/RG.2.1.3761.2008

Pugh, D. and P. Woodworth - Sea level science;
    Cambridge University Press, 2014

https://github.com/wesleybowman/UTide
"""
from .admin import __author__, __author_email__, __version__

from .analysers import run_utide_solve, constit_segment, tide_and_setup, analyse_long_series

from .parsers import parse_utide
