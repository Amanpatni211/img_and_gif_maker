# Geospatial Data Visualization Tool

A flexible tool for creating visualizations and animations from geospatial data files (NetCDF, GeoTIFF).

## Features

- Support for multiple data formats (NetCDF, GeoTIFF)
- Configurable visualization parameters
- Customizable date ranges
- Output options for individual frames and GIF animations
- Progress tracking
- Memory-efficient processing

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd img_and_gif_maker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your data files in the `data` directory

2. Configure visualization parameters in `config/default_config.yaml`:
   - Set input folder and file pattern
   - Configure date range
   - Adjust visualization parameters
   - Set output options

3. Run the script:
```bash
python src/run.py --config config/default_config.yaml
```

## Configuration Options

The YAML configuration file supports the following options:

```yaml
data:
  input_folder: "data"  # Folder containing input files
  file_pattern: "*.nc4"  # File pattern to match
  variable_name: "MWprecipitation"  # Variable name in the data file
  data_type: "nc4"  # Supported: nc4, netcdf, geotiff

date_range:
  start: "1998-06-01"
  end: "1998-10-01"

visualization:
  region:
    lon_min: 40
    lon_max: 120
    lat_min: -35
    lat_max: 40
  colormap: "RdYlBu_r"
  normalization:
    type: "log"  # Options: linear, log, custom
    vmin: 0.1
    vmax: 100
  figure:
    size: [12, 10]
    dpi: 150
  map_features:
    coastline: true
    borders: true
    land: true
    ocean: true
    gridlines: true
  title:
    enabled: true
    text: "IMERG Daily Precipitation"
    date_format: "%d %B %Y"

output:
  images:
    enabled: true
    folder: "output/images"
    format: "png"
  gif:
    enabled: true
    folder: "output/animations"
    filename: "animation.gif"
    duration: 0.25  # seconds per frame
    loop: 0  # 0 for infinite loop
```

## Example

For precipitation data:
```yaml
data:
  input_folder: "imerg_data"
  file_pattern: "*.nc4"
  variable_name: "MWprecipitation"
  data_type: "nc4"

visualization:
  normalization:
    type: "log"
    vmin: 0.1
    vmax: 100
```

## Output

The tool will create:
- Individual frames in the specified output folder (if enabled)
- A GIF animation (if enabled)

## Contributing

Feel free to submit issues and enhancement requests!