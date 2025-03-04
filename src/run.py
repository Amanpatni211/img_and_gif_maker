import argparse
import os
from processor import DataProcessor

def main():
    parser = argparse.ArgumentParser(description='Process geospatial data and create visualizations')
    parser.add_argument('--config', type=str, default='config/default_config.yaml',
                      help='Path to configuration YAML file')
    args = parser.parse_args()
    
    if not os.path.exists(args.config):
        print(f"Error: Configuration file not found at {args.config}")
        return
    
    try:
        processor = DataProcessor(args.config)
        processor.process_files()
    except Exception as e:
        print(f"Error processing files: {str(e)}")

if __name__ == '__main__':
    main()