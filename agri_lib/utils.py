"""
Utility functions for Agriculture and Forestry Library
"""
from datetime import datetime
from typing import Dict

def calculate_yield_estimate(area: float, crop_type: str, is_organic: bool = False) -> Dict:
    """
    Calculate yield estimate for a given area and crop type
    
    Args:
        area: Area in hectares
        crop_type: Type of crop (wheat, corn, rice, etc.)
        is_organic: Whether organic farming methods are used
    
    Returns:
        Dictionary with yield estimate and value
    """
    yield_rates = {
        'wheat': 3.5,
        'corn': 10.0,
        'rice': 4.5,
        'potato': 40.0,
        'soybean': 2.8,
        'cotton': 1.8,
        'pine': 15.0,
        'oak': 8.0,
        'eucalyptus': 25.0
    }
    
    prices = {
        'wheat': 250,
        'corn': 200,
        'rice': 350,
        'potato': 150,
        'soybean': 400,
        'cotton': 1500,
        'pine': 100,
        'oak': 150,
        'eucalyptus': 80
    }
    
    rate = yield_rates.get(crop_type.lower(), 5.0)
    price = prices.get(crop_type.lower(), 200)
    
    estimated_yield = area * rate
    if is_organic:
        estimated_yield *= 0.8
        price *= 1.3
    
    return {
        'yield_tonnes': round(estimated_yield, 2),
        'estimated_value': round(estimated_yield * price, 2),
        'per_hectare_yield': rate,
        'unit': 'tonnes' if crop_type.lower() not in ['pine', 'oak', 'eucalyptus'] else 'cubic_meters'
    }


def get_season_recommendation(month: int = None) -> Dict:
    """
    Get seasonal recommendations for farming activities
    
    Args:
        month: Month number (1-12). Uses current month if not provided.
    
    Returns:
        Dictionary with seasonal recommendations
    """
    if month is None:
        month = datetime.now().month
    
    recommendations = {
        1: {
            'season': 'Winter',
            'activities': ['Plan crop rotation', 'Order seeds', 'Maintain equipment', 'Prune fruit trees'],
            'crops_to_plant': ['Winter vegetables in greenhouse'],
            'forestry_tasks': ['Tree pruning', 'Firewood preparation']
        },
        2: {
            'season': 'Late Winter',
            'activities': ['Prepare seedbeds', 'Test soil', 'Plan irrigation'],
            'crops_to_plant': ['Early potatoes', 'Onions'],
            'forestry_tasks': ['Prepare for spring planting']
        },
        3: {
            'season': 'Early Spring',
            'activities': ['Start planting', 'Apply fertilizers', 'Prepare irrigation systems'],
            'crops_to_plant': ['Wheat', 'Barley', 'Peas', 'Carrots'],
            'forestry_tasks': ['Plant new trees', 'Check for winter damage']
        },
        4: {
            'season': 'Spring',
            'activities': ['Continue planting', 'Weed control', 'Pest monitoring'],
            'crops_to_plant': ['Corn', 'Soybeans', 'Cotton'],
            'forestry_tasks': ['Continue planting', 'Mulching']
        },
        5: {
            'season': 'Late Spring',
            'activities': ['Irrigate regularly', 'Fertilize', 'Monitor pests'],
            'crops_to_plant': ['Vegetables', 'Rice (paddies)'],
            'forestry_tasks': ['Monitor growth', 'Pest control']
        },
        6: {
            'season': 'Early Summer',
            'activities': ['Intensive pest management', 'Irrigation', 'First harvests'],
            'crops_to_plant': ['Second crop vegetables'],
            'forestry_tasks': ['Fire prevention', 'Thinning']
        },
        7: {
            'season': 'Summer',
            'activities': ['Harvest early crops', 'Manage water carefully', 'Store produce'],
            'crops_to_plant': ['Fall vegetables'],
            'forestry_tasks': ['Fire watch', 'Irrigation if needed']
        },
        8: {
            'season': 'Late Summer',
            'activities': ['Continue harvesting', 'Prepare for fall planting', 'Soil amendments'],
            'crops_to_plant': ['Winter wheat', 'Cover crops'],
            'forestry_tasks': ['Assess timber ready for harvest']
        },
        9: {
            'season': 'Early Autumn',
            'activities': ['Major harvest season', 'Plant cover crops', 'Soil testing'],
            'crops_to_plant': ['Garlic', 'Winter rye', 'Clover'],
            'forestry_tasks': ['Begin selective harvesting', 'Seed collection']
        },
        10: {
            'season': 'Autumn',
            'activities': ['Complete harvests', 'Prepare fields for winter', 'Equipment maintenance'],
            'crops_to_plant': ['Winter crops'],
            'forestry_tasks': ['Harvesting season', 'Plant deciduous trees']
        },
        11: {
            'season': 'Late Autumn',
            'activities': ['Final harvests', 'Cover crops', 'Winterize equipment'],
            'crops_to_plant': ['Greenhouse crops only'],
            'forestry_tasks': ['Complete harvesting', 'Prepare for winter']
        },
        12: {
            'season': 'Early Winter',
            'activities': ['Planning for next year', 'Record keeping', 'Market planning'],
            'crops_to_plant': ['Indoor/greenhouse only'],
            'forestry_tasks': ['Planning', 'Winter protection for young trees']
        }
    }
    
    return recommendations.get(month, recommendations[1])


def calculate_carbon_footprint(area: float, crop_type: str) -> Dict:
    """
    Calculate approximate carbon footprint for farming operation
    
    Args:
        area: Area in hectares
        crop_type: Type of crop or forest
    
    Returns:
        Dictionary with carbon footprint data
    """
    # CO2 emissions in tonnes per hectare per year
    emissions = {
        'wheat': 0.5,
        'corn': 0.8,
        'rice': 1.5,  # Higher due to methane
        'potato': 0.4,
        'soybean': 0.3,
        'cotton': 0.7
    }
    
    # CO2 sequestration for forestry
    sequestration = {
        'pine': 8.0,
        'oak': 6.5,
        'eucalyptus': 15.0,
        'teak': 7.0,
        'bamboo': 12.0
    }
    
    crop_lower = crop_type.lower()
    
    if crop_lower in sequestration:
        return {
            'type': 'carbon_sink',
            'annual_sequestration': round(area * sequestration[crop_lower], 2),
            'unit': 'tonnes_CO2_per_year',
            'climate_impact': 'positive'
        }
    else:
        emission_rate = emissions.get(crop_lower, 0.5)
        return {
            'type': 'carbon_source',
            'annual_emissions': round(area * emission_rate, 2),
            'unit': 'tonnes_CO2_per_year',
            'climate_impact': 'negative'
        }
