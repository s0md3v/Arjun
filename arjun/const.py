"""Constants used by Arjun."""
from arjun.core.colors import end, green, white

__version__ = '1.4'

BANNER = """
{}    _         
   /_| _ '    
  (  |/ /(//) {}v{}{}
      _/      {}\n""".format(
    green, white, __version__, green, end
)
