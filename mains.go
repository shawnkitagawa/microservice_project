package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"net/http"
	"sync"
	"time"
)

func printMapWithIndentation(m map[string]any, indent string) {
	for key, value := range m {
		switch v := value.(type) {
		case map[string]any:
			fmt.Println(indent + key + ":")
			printMapWithIndentation(v, indent+"  ")
		case []any:
			fmt.Println(indent + key + ":")
			for i, item := range v {
				fmt.Printf("%s  [%d]: %v\n", indent, i, item)
			}
		default:
			fmt.Printf("%s%s: %v\n", indent, key, value)
		}
	}
}

func concurrentWrite(ids []string, times []time.Time) {
	var wg sync.WaitGroup

	for _, id := range ids {
		for _, timestamp := range times {
			wg.Add(1)
			go func(id string, time time.Time) {
				defer wg.Done()
				status, body, err := poster(id, time)
				if err != nil {
					fmt.Printf("ISSUE: %d code, %s message, %s error\n", status, body, err.Error())
				} else {
					fmt.Printf("SUCCESS: %d code, %s message\n", status, body)
				}
			}(id, timestamp)
		}
	}

	wg.Wait()
}

func main() {
	ids := []string{"id1", "id2", "id3"}

	times := []time.Time{
		time.Date(2024, 1, 25, 20, 34, 6, 0, time.Local),
		time.Date(2024, 2, 8, 20, 34, 6, 0, time.Local),
		time.Date(2024, 2, 22, 20, 34, 6, 0, time.Local),
		time.Date(2024, 1, 31, 20, 34, 6, 0, time.Local),
		time.Date(2024, 1, 23, 20, 34, 6, 0, time.Local),
		time.Date(2024, 1, 29, 20, 34, 6, 0, time.Local),
		time.Date(2024, 2, 21, 20, 34, 6, 0, time.Local),
		time.Date(2024, 2, 12, 20, 34, 6, 0, time.Local),
		time.Date(2024, 2, 10, 20, 34, 6, 0, time.Local),
		time.Date(2024, 2, 17, 20, 34, 6, 0, time.Local),
		time.Date(2024, 2, 14, 20, 34, 6, 0, time.Local),
		time.Date(2024, 2, 19, 20, 34, 6, 0, time.Local),
		time.Date(2024, 2, 9, 20, 34, 6, 0, time.Local),
		time.Date(2024, 1, 23, 20, 34, 6, 0, time.Local),
		time.Date(2023, 2, 12, 20, 34, 6, 0, time.Local),
		time.Date(2023, 10, 22, 10, 34, 6, 0, time.Local),
		time.Date(2024, 2, 22, 4, 34, 6, 0, time.Local),
		time.Date(2024, 2, 22, 1, 34, 6, 0, time.Local),
		time.Date(2024, 2, 22, 4, 50, 6, 0, time.Local),
		time.Date(2024, 2, 22, 3, 50, 6, 0, time.Local),
		time.Date(2024, 2, 22, 3, 22, 6, 0, time.Local),
		time.Date(2024, 2, 22, 3, 22, 6, 0, time.Local),
		time.Date(2024, 2, 22, 3, 8, 6, 0, time.Local),
		time.Date(2024, 2, 24, 5, 8, 6, 0, time.Local),
		time.Date(2024, 2, 24, 4, 8, 6, 0, time.Local),
		time.Date(2024, 2, 24, 5, 8, 6, 0, time.Local),
		time.Date(2024, 2, 24, 4, 8, 6, 0, time.Local),
	}

	// concurrentWrite(ids, times) // Uncomment to test concurrently writing to api

	for _, id := range ids {
		for _, time := range times {
			status, body, err := poster(id, time)
			if err != nil {
				fmt.Printf("ISSUE: %d code, %s message, %s error\n", status, body, err.Error())
			} else {
				fmt.Printf("SUCCESS: %d code, %s message\n", status, body)
			}
		}
	}

	for _, id := range ids {

		hourlydata, err := getdata("http://127.0.0.1:5000/clicks_last_day_by_hour/" + id)
		if err != nil {
			fmt.Printf("Error getting hourly data for %s, error: %s\n", id, err.Error())
		} else {
			fmt.Printf("Hourly data for %s: \n", id)
			printMapWithIndentation(hourlydata, "   ")
		}

		dailydata, err := getdata("http://127.0.0.1:5000/clicks_last_week_by_day/" + id)
		if err != nil {
			fmt.Printf("Error getting daily data for %s, error: %s\n", id, err.Error())
		} else {
			fmt.Printf("Daily data for %s: \n", id)
			printMapWithIndentation(dailydata, "   ")
		}

		weeklydata, err := getdata("http://127.0.0.1:5000/clicks_last_month_by_week/" + id)
		if err != nil {
			fmt.Printf("Error getting weekly data for %s, error: %s\n", id, err.Error())
		} else {
			fmt.Printf("Weekly data for %s: \n", id)
			printMapWithIndentation(weeklydata, "   ")
		}

	}
}

func getdata(url string) (map[string]any, error) {

	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, errors.New("unexpected status code")
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var result map[string]any
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, err
	}

	return result, nil

}
func poster(id string, time time.Time) (int, string, error) {
	url := "http://127.0.0.1:5000/analyze_qr_code"

	payload := map[string]interface{}{
		"qr_id":     id,
		"timestamp": time,
	}

	statusCode, responseBody, err := performPostRequest(url, payload)
	if err != nil {
		fmt.Println("Request failed:", err)
		return 0, "", err
	}

	return statusCode, responseBody, nil
}

func performPostRequest(url string, payload map[string]interface{}) (int, string, error) {
	jsonPayload, err := json.Marshal(payload)
	if err != nil {
		return 0, "", fmt.Errorf("error encoding JSON: %w", err)
	}

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonPayload))
	if err != nil {
		return 0, "", fmt.Errorf("error creating request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return 0, "", fmt.Errorf("error sending request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return resp.StatusCode, "", fmt.Errorf("error reading response body: %w", err)
	}

	return resp.StatusCode, string(body), nil
}
