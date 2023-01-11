class Clustering:
    
    item_dims: List[Tuple[float]]
    item_lat_long: List[Tuple[float]]
    no_riders: int
    rider_vol: float
    
    def __init__(self, item_dims: List[Tuple[float]], item_lat_long: List[Tuple[float]], no_riders: int, rider_vol: float) -> None:
        assert len(item_dims)>0
        assert len(item_dims)==len(item_lat_long)
        assert len(item_dims[0])==3
        assert len(item_lat_long[0])==2
        assert no_riders<len(item_dims)
        
        self.item_dims = item_dims
        self.item_lat_long = item_lat_long
        self.no_riders = no_riders
        self.rider_vol = rider_vol
    
    def distribute(self) -> List[List[int]]:
        
        """
        TODO: Implement this function
        """
        
        pass