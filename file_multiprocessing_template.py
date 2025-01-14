# custom exports
import pandas as pd
import csv
import sys
import os
from datetime import datetime
from multiprocessing import Pool, cpu_count

# load to dataframe
def load_mapping_table(file_path):
    df = pd.read_csv(file_path, usecols=[0, 1], dtype=str)  # Specify columns and types
    return df.set_index(df.columns[0])  # Set first column as the index

# pd dataframe
df = load_mapping_table('mapping_table.csv')

# get rid of duplicates
df = df.reset_index().drop_duplicates(subset='trackId').set_index('trackId')




def process_chunksize(input_file):
    # count number of lines in file to spread chunksize efficiently across cpu-cores
    with open(input_file, mode='r', newline='', encoding='utf-8') as file:

        print(f"Calculating chunk-size for multi-processing...")

        total_line_count = sum(1 for line in file) -1
        num_cores = cpu_count()
        chunk_size = max(1, total_line_count // num_cores)

        print(f"Total lines in file {input_file}: {total_line_count}, Cores: {num_cores}, Chunk size: {chunk_size}")



def process_chunk(lines):

    results = []
    for line in lines:

        # Process single line
        trackId = line["trackId"]
        leadId = None
        target_row = {}

        try:
            leadId = df.at[trackId, "leadId"]
            target_row["leadId"] = leadId
            
        except Exception as e:
            pass

        else:
            target_row["leadId"] = leadId
            target_row.update(line)
            results.append(target_row)



    return results


def read_csv_in_chunks(input_file, chunk_size=10000):

    with open(input_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        header = reader.fieldnames

        chunk = []

        for line in reader:
            chunk.append(line)
            if len(chunk) == chunk_size:
                yield chunk, header
                chunk = []

        if chunk:
            yield chunk, header


def process_and_write(input_file, output_file, chunk_size=10000):

    # Create or truncate the output file and write the header
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = None
        for chunk, header in read_csv_in_chunks(input_file, chunk_size):
            with Pool(cpu_count()) as pool:
                processed_chunks = pool.map(process_chunk, [chunk])

            processed_rows = [row for sublist in processed_chunks for row in sublist]

            if writer is None:  # Initialize the writer with header
                writer = csv.DictWriter(file, fieldnames=["leadId"] + header)
                writer.writeheader()

            writer.writerows(processed_rows)


def main():

    input_dir = "input_exports"
    output_dir = "output_exports"

    # Process all CSV files in the input directory
    for input_file in os.listdir(input_dir):
        if input_file.endswith(".csv"):
            input_path = os.path.join(input_dir, input_file)
            output_path = os.path.join(output_dir, f"processed_{input_file}")
            print(f"{datetime.now()}  --  Processing {input_path} -> {output_path}")
            process_and_write(input_path, output_path, chunk_size=process_chunksize(input_path))
            print(f"INFO -- {datetime.now()} - Finished processing file {output_path} \n")



if __name__ == "__main__":
    main()
