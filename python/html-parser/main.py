import lxml.html
import lxml.etree

from benchmark import read_html_file, run_performance_test

html_file = "example.html"
html_file_large = "example-large.html"


# Function to generate large html file by duplicating the <div id="main"> block
def duplicate_div_main(input_file, output_file, times=100):
    parser = lxml.etree.HTMLParser(encoding="utf-8")
    tree = lxml.etree.parse(input_file, parser=parser)
    main_div = tree.xpath("//div[@id='main']")[0]
    duplicated_content = "".join([lxml.html.tostring(main_div, encoding="unicode") for _ in range(times)])
    main_div.getparent().replace(main_div, lxml.html.fromstring(duplicated_content))
    tree.write(output_file, encoding="utf-8", method="html")


# Test with the original HTML
print("Start resolving the original HTML...")
html_content = read_html_file(html_file)
results = run_performance_test(html_content, 100)

print("Execution time of the original HTML (seconds):")
print("-" * 50)
selectolax_time = results["selectolax"]
for parser, avg_time in results.items():
    ratio = avg_time / selectolax_time
    print(f"{parser:15}: {avg_time:.6f} ({ratio:.2f}x)")


# Test with the large HTML
print("\nStart resolving the large HTML...")
duplicate_div_main(html_file, html_file_large)
html_content = read_html_file(html_file_large)
results = run_performance_test(html_content, 1)

print("Execution time of the large HTML (seconds):")
print("-" * 50)
selectolax_time = results["selectolax"]
for parser, avg_time in results.items():
    ratio = avg_time / selectolax_time
    print(f"{parser:15}: {avg_time:.6f} ({ratio:.2f}x)")
