"""
Crop Manager Module - Core OOP functionality for Agriculture and Forestry management
"""
from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Dict, Optional

class BasePlant(ABC):
    """Abstract base class for all plants"""
    
    def __init__(self, name: str, area: float):
        self._name = name
        self._area = area
        self._planting_date = datetime.now()
        self._status = 'planted'
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def area(self) -> float:
        return self._area
    
    @area.setter
    def area(self, value: float):
        if value <= 0:
            raise ValueError("Area must be positive")
        self._area = value
    
    @property
    def status(self) -> str:
        return self._status
    
    @status.setter
    def status(self, value: str):
        valid_statuses = ['planted', 'growing', 'harvesting', 'harvested', 'dormant']
        if value not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        self._status = value
    
    @abstractmethod
    def get_yield_estimate(self) -> float:
        """Calculate estimated yield based on area and type"""
        pass
    
    @abstractmethod
    def get_type(self) -> str:
        """Return the type of plant"""
        pass
    
    def days_since_planting(self) -> int:
        """Calculate days since planting"""
        return (datetime.now() - self._planting_date).days
    
    def to_dict(self) -> Dict:
        """Convert to dictionary representation"""
        return {
            'name': self._name,
            'area': self._area,
            'status': self._status,
            'type': self.get_type(),
            'days_planted': self.days_since_planting()
        }


class Crop(BasePlant):
    """Class representing an agricultural crop"""
    
    # Yield estimates in tonnes per hectare for common crops
    YIELD_RATES = {
        'wheat': 3.5,
        'corn': 10.0,
        'rice': 4.5,
        'potato': 40.0,
        'soybean': 2.8,
        'cotton': 1.8,
        'default': 5.0
    }
    
    def __init__(self, name: str, area: float, crop_subtype: str = 'default'):
        super().__init__(name, area)
        self._crop_subtype = crop_subtype.lower()
    
    def get_yield_estimate(self) -> float:
        """Calculate estimated yield in tonnes"""
        rate = self.YIELD_RATES.get(self._crop_subtype, self.YIELD_RATES['default'])
        return self._area * rate
    
    def get_type(self) -> str:
        return 'agriculture'
    
    def get_water_requirement(self) -> float:
        """Estimate water requirement in cubic meters per hectare"""
        water_needs = {
            'wheat': 4500,
            'corn': 5000,
            'rice': 12000,
            'potato': 5000,
            'soybean': 4500,
            'cotton': 7000,
            'default': 5000
        }
        rate = water_needs.get(self._crop_subtype, water_needs['default'])
        return self._area * rate


class Forest(BasePlant):
    """Class representing a forestry plantation"""
    
    # Timber yield in cubic meters per hectare
    TIMBER_RATES = {
        'pine': 15.0,
        'oak': 8.0,
        'eucalyptus': 25.0,
        'teak': 10.0,
        'bamboo': 20.0,
        'default': 12.0
    }
    
    def __init__(self, name: str, area: float, tree_type: str = 'default'):
        super().__init__(name, area)
        self._tree_type = tree_type.lower()
    
    def get_yield_estimate(self) -> float:
        """Calculate estimated timber yield in cubic meters"""
        rate = self.TIMBER_RATES.get(self._tree_type, self.TIMBER_RATES['default'])
        return self._area * rate
    
    def get_type(self) -> str:
        return 'forestry'
    
    def get_carbon_sequestration(self) -> float:
        """Estimate annual carbon sequestration in tonnes CO2"""
        # Average carbon sequestration rates in tonnes CO2 per hectare per year
        carbon_rates = {
            'pine': 8.0,
            'oak': 6.5,
            'eucalyptus': 15.0,
            'teak': 7.0,
            'bamboo': 12.0,
            'default': 8.0
        }
        rate = carbon_rates.get(self._tree_type, carbon_rates['default'])
        return self._area * rate


class Agriculture(Crop):
    """Extended agriculture class with additional features"""
    
    def __init__(self, name: str, area: float, crop_subtype: str = 'default', is_organic: bool = False):
        super().__init__(name, area, crop_subtype)
        self._is_organic = is_organic
    
    def get_yield_estimate(self) -> float:
        """Organic farming typically yields 20% less"""
        base_yield = super().get_yield_estimate()
        if self._is_organic:
            return base_yield * 0.8
        return base_yield
    
    def get_market_value(self) -> float:
        """Estimate market value (organic premium of 30%)"""
        base_prices = {
            'wheat': 250,
            'corn': 200,
            'rice': 350,
            'potato': 150,
            'soybean': 400,
            'cotton': 1500,
            'default': 300
        }
        price = base_prices.get(self._crop_subtype, base_prices['default'])
        yield_tonnes = self.get_yield_estimate()
        
        if self._is_organic:
            return yield_tonnes * price * 1.3
        return yield_tonnes * price


class CropManager:
    """Manager class for handling multiple crops/forests"""
    
    def __init__(self):
        self._plants: List[BasePlant] = []
    
    def add_crop(self, name: str, plant_type: str, area: float, subtype: str = 'default'):
        """Add a new crop or forest to the manager"""
        if plant_type.lower() == 'agriculture':
            plant = Crop(name, area, subtype)
        elif plant_type.lower() == 'forestry':
            plant = Forest(name, area, subtype)
        else:
            plant = Crop(name, area, subtype)
        
        self._plants.append(plant)
        return plant
    
    def remove_crop(self, name: str) -> bool:
        """Remove a crop by name"""
        for i, plant in enumerate(self._plants):
            if plant.name == name:
                del self._plants[i]
                return True
        return False
    
    def get_all_crops(self) -> List[BasePlant]:
        """Get all crops"""
        return self._plants
    
    def get_crops_by_type(self, plant_type: str) -> List[BasePlant]:
        """Filter crops by type"""
        return [p for p in self._plants if p.get_type() == plant_type.lower()]
    
    def get_total_area(self) -> float:
        """Calculate total area under management"""
        return sum(p.area for p in self._plants)
    
    def get_total_yield_estimate(self) -> float:
        """Calculate total estimated yield"""
        return sum(p.get_yield_estimate() for p in self._plants)


class CropAnalyzer:
    """Analyzer class for generating insights from crop data"""
    
    def __init__(self, crop_manager: CropManager):
        self._manager = crop_manager
    
    def get_statistics(self) -> Dict:
        """Get basic statistics"""
        crops = self._manager.get_all_crops()
        agriculture = self._manager.get_crops_by_type('agriculture')
        forestry = self._manager.get_crops_by_type('forestry')
        
        return {
            'total_crops': len(crops),
            'total_area': round(self._manager.get_total_area(), 2),
            'agriculture_count': len(agriculture),
            'forestry_count': len(forestry),
            'agriculture_area': round(sum(c.area for c in agriculture), 2),
            'forestry_area': round(sum(f.area for f in forestry), 2),
            'total_yield_estimate': round(self._manager.get_total_yield_estimate(), 2)
        }
    
    def get_detailed_analysis(self) -> Dict:
        """Get detailed analysis including recommendations"""
        stats = self.get_statistics()
        crops = self._manager.get_all_crops()
        
        analysis = {
            'statistics': stats,
            'crops_detail': [c.to_dict() for c in crops],
            'recommendations': [],
            'risk_assessment': 'low'
        }
        
        # Generate recommendations
        if stats['total_area'] == 0:
            analysis['recommendations'].append('Start by adding your first crop or forest plantation.')
        else:
            if stats['agriculture_count'] > 0 and stats['forestry_count'] == 0:
                analysis['recommendations'].append('Consider adding forestry for carbon sequestration and diversification.')
            
            if stats['forestry_count'] > 0:
                # Calculate carbon sequestration
                forestry_plants = self._manager.get_crops_by_type('forestry')
                total_carbon = sum(f.get_carbon_sequestration() for f in forestry_plants if isinstance(f, Forest))
                analysis['carbon_sequestration'] = round(total_carbon, 2)
                analysis['recommendations'].append(f'Your forests sequester approximately {round(total_carbon, 2)} tonnes of CO2 per year.')
            
            if stats['total_area'] > 100:
                analysis['recommendations'].append('Consider implementing precision agriculture techniques for large-scale management.')
            
            # Diversification check
            if len(crops) == 1:
                analysis['recommendations'].append('Diversify your crops to reduce risk from market fluctuations and pests.')
                analysis['risk_assessment'] = 'medium'
            elif len(crops) >= 3:
                analysis['risk_assessment'] = 'low'
                analysis['recommendations'].append('Good crop diversification! This reduces overall risk.')
        
        return analysis
    
    def get_seasonal_advice(self, current_month: int = None) -> str:
        """Get seasonal advice based on current month"""
        if current_month is None:
            current_month = datetime.now().month
        
        seasons = {
            (12, 1, 2): 'Winter: Focus on planning next season, soil preparation, and pruning dormant trees.',
            (3, 4, 5): 'Spring: Ideal time for planting most crops. Monitor soil moisture and prepare irrigation.',
            (6, 7, 8): 'Summer: Focus on pest management, irrigation, and early harvesting of some crops.',
            (9, 10, 11): 'Autumn: Harvest season for most crops. Prepare soil for winter crops.'
        }
        
        for months, advice in seasons.items():
            if current_month in months:
                return advice
        
        return 'Monitor your crops regularly and adjust care based on weather conditions.'
