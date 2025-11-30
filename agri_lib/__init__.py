"""
Agriculture and Forestry Library
Custom OOP library providing meaningful functionality for crop management and analysis
"""

from .crop_manager import CropManager, CropAnalyzer, Crop, Forest, Agriculture
from .utils import calculate_yield_estimate, get_season_recommendation

__version__ = '1.0.0'
__all__ = ['CropManager', 'CropAnalyzer', 'Crop', 'Forest', 'Agriculture', 
           'calculate_yield_estimate', 'get_season_recommendation']
