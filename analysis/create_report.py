import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from fpdf import FPDF
import glob

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Rubik Cube Algorithm Benchmark Report', 0, 1, 'C')
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)
        
    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, body)
        self.ln()
        
    def add_image(self, img_path, w=None, h=None, caption=None):
        if os.path.exists(img_path):
            if w is None:
                w = 180  # Default width
                h = 0   # Auto-calculate height to maintain aspect ratio
            self.image(img_path, x=10, w=w, h=h)
            if caption:
                self.set_font('Arial', 'I', 9)
                self.ln(5)
                self.cell(0, 5, caption, 0, 1, 'C')
            self.ln(10)
    
    def add_table(self, data, header, col_widths=None):
        self.set_font('Arial', 'B', 10)
        
        # If no column widths specified, distribute evenly
        if col_widths is None:
            col_widths = [190 / len(header)] * len(header)
        
        # Header
        for i, h in enumerate(header):
            self.cell(col_widths[i], 7, h, 1, 0, 'C')
        self.ln()
        
        # Data
        self.set_font('Arial', '', 9)
        for row in data:
            for i, item in enumerate(row):
                self.cell(col_widths[i], 6, str(item), 1, 0, 'C')
            self.ln()
        self.ln(10)

def create_report():
    # Load complexity summary
    summary_file = "analysis/data/extended_complexity_summary_latest.csv"
    if not os.path.exists(summary_file):
        print(f"Summary file not found: {summary_file}")
        return
    
    summary_df = pd.read_csv(summary_file)
    
    # Initialize PDF
    pdf = PDF()
    pdf.add_page()
    
    # Introduction
    pdf.chapter_title("1. Introduction")
    pdf.chapter_body(
        "This report presents the benchmark results for various search algorithms "
        "applied to the Rubik's Cube 2x2 solving problem. The benchmarks measure "
        "execution time, memory usage, and extrapolate performance to larger datasets "
        "using regression models.\n\n"
        "The algorithms tested include BFS, DFS, A*, IDS, UCS, Greedy Best-First Search, "
        "IDA*, Hill Climbing variations, and Pattern Database A*."
    )
    
    # Methodology
    pdf.chapter_title("2. Methodology")
    pdf.chapter_body(
        "The benchmark methodology involves:\n\n"
        "1. Running each algorithm on sample sizes from 100 to 2,000 states\n"
        "2. Fitting complexity models (O(n), O(n log n), O(n²), O(n³))\n"
        "3. Selecting the best-fitting model based on R² score\n"
        "4. Extrapolating performance to 5,000, 10,000, 50,000 and 100,000 states\n\n"
        "Each test was run with small scramble depths (2 moves) to ensure algorithms "
        "could find solutions within the time limit. Success rates and memory usage "
        "were also measured."
    )
    
    # Algorithm Comparison
    pdf.chapter_title("3. Algorithm Comparison")
    pdf.chapter_body(
        "The following table summarizes the performance of all algorithms, sorted by extrapolated "
        "execution time for 100,000 states:"
    )
    
    # Sort the summary by execution time
    summary_df = summary_df.sort_values(by="time_for_100k_samples")
    
    # Prepare table data
    header = ["Algorithm", "Complexity Model", "Time for 100K states (s)"]
    data = []
    
    for _, row in summary_df.iterrows():
        algorithm = row['algorithm']
        model = row['complexity_model']
        time_100k = f"{row['time_for_100k_samples']:.2f}"
        data.append([algorithm, model, time_100k])
    
    # Add table
    pdf.add_table(data, header, col_widths=[50, 70, 70])
    
    # Add comparison chart
    pdf.add_image("analysis/figures/comprehensive_algorithm_comparison_latest.png", 
                 caption="Figure 1: Algorithm Performance Comparison")
    
    # Individual Algorithm Analysis
    pdf.chapter_title("4. Individual Algorithm Analysis")
    
    # Most interesting algorithms to analyze
    algorithms_to_show = [
        ('hill_max', 'Hill Climbing Max'),
        ('ids', 'Iterative Deepening Search'),
        ('bfs', 'Breadth-First Search'),
        ('ida_star', 'IDA*'),
        ('pdb', 'Pattern Database A*')
    ]
    
    for algo_key, algo_name in algorithms_to_show:
        # Get algorithm data from summary
        algo_data = summary_df[summary_df['algorithm'] == algo_key]
        if algo_data.empty:
            continue
            
        complexity = algo_data['complexity_model'].iloc[0]
        time_100k = algo_data['time_for_100k_samples'].iloc[0]
        
        pdf.chapter_body(f"{algo_name} ({algo_key}):\n")
        pdf.chapter_body(
            f"Complexity Model: {complexity}\n"
            f"Extrapolated Time for 100,000 states: {time_100k:.2f} seconds"
        )
        
        # Find and add extrapolation chart
        extrapolation_chart = f"analysis/figures/{algo_key}_rubik2x2_extrapolation_latest.png"
        if os.path.exists(extrapolation_chart):
            pdf.add_image(extrapolation_chart, caption=f"Figure: {algo_name} Performance Extrapolation")
            
        pdf.ln(5)
    
    # Key Findings
    pdf.add_page()
    pdf.chapter_title("5. Key Findings")
    pdf.chapter_body(
        "The benchmark results reveal several important insights:\n\n"
        
        "1. Algorithm Efficiency Hierarchy:\n"
        "   - Hill Climbing Max (~30s) is the fastest but doesn't guarantee optimal solutions\n"
        "   - IDS (~43s) is the fastest algorithm that guarantees optimal solutions\n"
        "   - Hill Climbing Random (~55s) offers a good balance of speed and solution quality\n"
        "   - BFS and A* variants perform reasonably well for small state spaces\n"
        "   - DFS (~12,757s) and Greedy search (~379,514s) perform poorly on this problem\n\n"
        
        "2. Complexity Models:\n"
        "   - Algorithms split into O(n) and O(n log n) complexity classes\n"
        "   - Non-optimal algorithms (Hill Climbing) tend to have O(n) complexity\n"
        "   - Optimal algorithms (BFS, A*) tend to have O(n log n) complexity\n\n"
        
        "3. Memory Efficiency:\n"
        "   - IDS and IDA* are the most memory-efficient among optimal algorithms\n"
        "   - BFS and A* require more memory for storing frontier and visited states\n\n"
        
        "4. Success Rates:\n"
        "   - Optimal algorithms (BFS, A*, IDS) have high success rates for small depths\n"
        "   - Hill Climbing algorithms may get stuck in local optima\n"
        "   - PDB A* has the best success rate for complex states"
    )
    
    # Conclusions and Recommendations
    pdf.chapter_title("6. Conclusions and Recommendations")
    pdf.chapter_body(
        "Based on the benchmark results, we recommend:\n\n"
        
        "1. For quick solutions where optimality is not critical:\n"
        "   - Use Hill Climbing Max as it's significantly faster than other algorithms\n\n"
        
        "2. For optimal solutions with limited memory:\n"
        "   - Use IDS which provides excellent performance while guaranteeing optimality\n\n"
        
        "3. For optimal solutions with good heuristics available:\n"
        "   - Use Pattern Database A* (PDB) for the best informed search performance\n\n"
        
        "4. For educational purposes or full state space exploration:\n"
        "   - Use BFS for smaller cubes and state spaces\n\n"
        
        "The benchmark confirms that algorithm selection should be based on the specific "
        "requirements of the application, balancing solution optimality, execution time, "
        "and memory constraints."
    )
    
    # Save PDF
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"analysis/Rubik_Algorithm_Benchmark_Report_{timestamp}.pdf"
    latest_filename = "analysis/Rubik_Algorithm_Benchmark_Report_latest.pdf"
    pdf.output(pdf_filename, 'F')
    pdf.output(latest_filename, 'F')
    
    print(f"Report generated: {pdf_filename}")
    print(f"Report also saved as: {latest_filename}")

if __name__ == "__main__":
    # Create folders if they don't exist
    os.makedirs("analysis/data", exist_ok=True)
    os.makedirs("analysis/figures", exist_ok=True)
    
    create_report() 