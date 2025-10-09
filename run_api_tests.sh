#!/bin/bash
echo "Running MobixAI API Tests..."
echo "============================="
python test_all_apis.py
echo "============================="
echo "API tests completed."
read -p "Press any key to continue..."