import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os
from glob import glob
import numpy as np
from datetime import datetime
import imageio.v2 as imageio
from tqdm import tqdm
import gc
import yaml
import rasterio
from pathlib import Path

class DataProcessor:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self._setup_directories()
        
    def _setup_directories(self):
        """Create necessary output directories."""
        if self.config['output']['images']['enabled']:
            os.makedirs(self.config['output']['images']['folder'], exist_ok=True)
        if self.config['output']['gif']['enabled']:
            os.makedirs(self.config['output']['gif']['folder'], exist_ok=True)
            
    def _get_date_from_filename(self, filename):
        """Extract date from filename based on data type."""
        if self.config['data']['data_type'] in ['nc4', 'netcdf']:
            # Extract date from filename like 'imerg_daily_19990101.nc4'
            date_str = os.path.basename(filename).split('_')[2].split('.')[0]
            return datetime.strptime(date_str, '%Y%m%d')
        elif self.config['data']['data_type'] == 'geotiff':
            # Implement GeoTIFF date extraction based on your naming convention
            date_str = os.path.basename(filename).split('_')[1].split('.')[0]
            return datetime.strptime(date_str, '%Y%m%d')
    
    def _load_data(self, file_path):
        """Load data based on file type."""
        if self.config['data']['data_type'] in ['nc4', 'netcdf']:
            ds = xr.open_dataset(file_path)
            data = ds[self.config['data']['variable_name']].squeeze()
            lons = data.lon.values
            lats = data.lat.values
        elif self.config['data']['data_type'] == 'geotiff':
            with rasterio.open(file_path) as src:
                data = src.read(1)
                lons = np.linspace(src.bounds.left, src.bounds.right, src.width)
                lats = np.linspace(src.bounds.bottom, src.bounds.top, src.height)
        return data, lons, lats
    
    def _create_normalization(self, data):
        """Create appropriate normalization based on config."""
        norm_type = self.config['visualization']['normalization']['type']
        vmin = self.config['visualization']['normalization']['vmin']
        vmax = self.config['visualization']['normalization']['vmax']
        
        if norm_type == 'log':
            return colors.LogNorm(vmin=vmin, vmax=vmax)
        elif norm_type == 'linear':
            return colors.Normalize(vmin=vmin, vmax=vmax)
        else:
            raise ValueError(f"Unsupported normalization type: {norm_type}")
    
    def _create_plot(self, data, lons, lats, date_str):
        """Create a single plot with the given data."""
        fig = plt.figure(figsize=self.config['visualization']['figure']['size'])
        ax = plt.axes(projection=ccrs.PlateCarree())
        
        # Set map extent
        ax.set_extent([
            self.config['visualization']['region']['lon_min'],
            self.config['visualization']['region']['lon_max'],
            self.config['visualization']['region']['lat_min'],
            self.config['visualization']['region']['lat_max']
        ], crs=ccrs.PlateCarree())
        
        # Create mesh grid
        lon_mesh, lat_mesh = np.meshgrid(lons, lats)
        
        # Plot data
        norm = self._create_normalization(data)
        im = ax.pcolormesh(lon_mesh, lat_mesh, data.T,
                          transform=ccrs.PlateCarree(),
                          cmap=self.config['visualization']['colormap'],
                          norm=norm)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, extend='both')
        cbar.set_label('Precipitation (mm/day)')
        
        # Add map features
        if self.config['visualization']['map_features']['coastline']:
            ax.add_feature(cfeature.COASTLINE, linewidth=1, edgecolor='black')
        if self.config['visualization']['map_features']['borders']:
            ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
        if self.config['visualization']['map_features']['land']:
            ax.add_feature(cfeature.LAND, alpha=0.1)
        if self.config['visualization']['map_features']['ocean']:
            ax.add_feature(cfeature.OCEAN, alpha=0.1)
        if self.config['visualization']['map_features']['gridlines']:
            gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
            gl.top_labels = False
            gl.right_labels = False
        
        # Set title
        if self.config['visualization']['title']['enabled']:
            date_obj = datetime.strptime(date_str, '%Y%m%d')
            formatted_date = date_obj.strftime(self.config['visualization']['title']['date_format'])
            plt.title(f"{self.config['visualization']['title']['text']}\n{formatted_date}", pad=20)
        
        return fig
    
    def process_files(self):
        """Process all files and create visualizations."""
        # Get list of files
        data_path = self.config['data']['input_folder']
        file_pattern = self.config['data']['file_pattern']
        nc_files = glob(os.path.join(data_path, file_pattern))
        
        # Filter files by date range
        start_date = datetime.strptime(self.config['date_range']['start'], '%Y-%m-%d')
        end_date = datetime.strptime(self.config['date_range']['end'], '%Y-%m-%d')
        
        filtered_files = []
        for file_path in sorted(nc_files):
            try:
                file_date = self._get_date_from_filename(file_path)
                if start_date <= file_date <= end_date:
                    filtered_files.append(file_path)
            except Exception as e:
                print(f"Warning: Could not process file {file_path}: {str(e)}")
                continue
        
        print(f"Found {len(filtered_files)} files in the date range")
        
        # Process each file
        frame_files = []
        try:
            for i, file_path in enumerate(tqdm(filtered_files, desc="Processing frames")):
                # Load data
                data, lons, lats = self._load_data(file_path)
                date_str = self._get_date_from_filename(file_path).strftime('%Y%m%d')
                
                # Create plot
                fig = self._create_plot(data, lons, lats, date_str)
                
                # Save frame if enabled
                if self.config['output']['images']['enabled']:
                    frame_path = os.path.join(
                        self.config['output']['images']['folder'],
                        f'frame_{i:03d}.{self.config["output"]["images"]["format"]}'
                    )
                    plt.savefig(frame_path, dpi=self.config['visualization']['figure']['dpi'],
                              bbox_inches='tight')
                    frame_files.append(frame_path)
                
                plt.close()
                gc.collect()
            
            # Create GIF if enabled
            if self.config['output']['gif']['enabled'] and frame_files:
                print("\nCreating GIF animation...")
                gif_path = os.path.join(
                    self.config['output']['gif']['folder'],
                    self.config['output']['gif']['filename']
                )
                with imageio.get_writer(gif_path, mode='I',
                                      duration=self.config['output']['gif']['duration'],
                                      loop=self.config['output']['gif']['loop']) as writer:
                    for frame_path in tqdm(frame_files, desc="Creating GIF"):
                        image = imageio.imread(frame_path)
                        writer.append_data(image)
                
                print(f"\nAnimation saved to: {gif_path}")
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            raise