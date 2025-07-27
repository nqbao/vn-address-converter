Please use the provided csv and use it to validate parse_address and convert_address to make sure it works correctly.

Please follow the below instructions
- Use the `test_csv_processor.py csvfile` to run evaluation, it will output error and summary. Never try to read the full file, it is too big for you to read.
- Try to generalize the patterns, look through the errors list to see what is the best way to approach
- For missing mapping:
  - if it is "hoà" vs "hòa" then try to fix it via manual aliases
  - Try to do web search to find the info, usually the mapping is posted on thuvienphapluat.vn
  - You can use the website vnpost to check what is the right result, then edit the ward mapping to add it
  - If it is a legacy mapping, use "legacy_district_mapping" or "legacy_ward_mapping"
- Never add a street address to the manual aliases
- If you stuck in the loop, just yield back to user to control
- Run `make test` at the end to make sure nothing is broken
- If possible, update tests.csv with some represenative test cases
- Continue to run test_csv_processor again to find if we can fix more problems.

Below are possible common errors you can skip
- If the input is not in the right format, if you think you can try improve parser then fix it, otherwise ignore
- You don't need to handle foreign street address
