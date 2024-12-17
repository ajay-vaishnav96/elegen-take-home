case "$1" in
    "place_order")
        # Code for part 1
        echo "Running part 1"
        # ...
          curl -X POST http://127.0.0.1:8080/place_order -H "Content-Type: application/json" -d '{
          "order": [
              {
                  "sample_uuid": "600b92a2-195e-495a-8135-56bc2b71441a",
                  "sequence": "ATGTACACTACGT"
              },
              {
                  "sample_uuid": "65482eb9-27ea-44c2-bc92-405ed90ad9d2",
                  "sequence": "GCCTAC"
              },
              {
                  "sample_uuid": "3f92802d-b84c-4dcc-856d-c1baeb908afd",
                  "sequence": "TAGTAGATAGCAGCATTAGACAT"
              }
          ]
      }'
        ;;
    "list_orders_to_process")
        # Code for part 2
        echo "Running part 2"
        # ...
         curl -X GET arn:aws:lambda:us-west-2:841162704319:function:elegen-take-home-dev/list_orders_to_process -H "Content-Type: application/json"
        ;;
    "log_qc_results")
      # Code for part 2
      echo "Running part 2"
      curl -X POST http://127.0.0.1:8080/log_qc_results -H "Content-Type: application/json" -d '{
        "samples_made": [
          {
              "sample_uuid": "600b92a2-195e-495a-8135-56bc2b71441a",
              "plate_id": 1337,
              "well": "A01",
              "qc_1": 17.5,
              "qc_2": 2.3,
              "qc_3": "PASS"
          },
          {
              "sample_uuid": "65482eb9-27ea-44c2-bc92-405ed90ad9d2",
              "plate_id": 1337,
              "well": "A02",
              "qc_1": 20.1,
              "qc_2": 9.2,
              "qc_3": "PASS"
          },
          {
              "sample_uuid": "3f92802d-b84c-4dcc-856d-c1baeb908afd",
              "plate_id": 1337,
              "well": "B01",
              "qc_1": 9.5,
              "qc_2": 7.3,
              "qc_3": "FAIL"
          }
        ]
      }'
      # ...
      ;;
    "list_samples_to_ship")
        # Code for part 2
        echo "Running part 2"
        curl -X GET http://127.0.0.1:8080/list_samples_to_ship -H "Content-Type: application/json"
        # ...
        ;;
    "record_samples_as_shipped")
        # Code for part 2
        echo "Running part 2"
        curl -X POST http://127.0.0.1:8080/record_samples_as_shipped -H "Content-Type: application/json" -d '{
           "samples_shipped": [
            "65482eb9-27ea-44c2-bc92-405ed90ad9d2"
          ]
        }'
        # ...
        ;;
    "report_sample_statuses")
        # Code for part 2
        echo "Running part 2"
        curl -X GET http://127.0.0.1:8080/report_sample_statuses -H "Content-Type: application/json" -d '
        {
          "order_uuid_to_get_sample_statuses_for": "913636ea-9c02-4152-9188-0ca8436f5330"
        }'
        # ...
        ;;
    *)
        echo "Invalid parameter. Use 'run_part1' or 'run_part2'"
        ;;
        
esac