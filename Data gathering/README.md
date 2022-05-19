# Intro

This is the very beginning of backtest. 

This part focuses on OHLC price data gathering for a specific trading pair, there are a lot of data services that sell what is needed, but for this particular project such data will be free to download using `Python3.x` `Selenium4.1.0`

# Procedure

To do so, you will first have to run `Chrome Browser` using **DevTools Protocol**, as shown down below:

* Run `cmd`
* Type: `cd your_chrome.exe_path`and press ↵Enter
* Type: `chrome.exe --remote-debugging-port=9222 --user-data-dir:"your_chrome_user_data_dir_path"` and press ↵Enter

*Note: You can get your_chrome_user_data_dir_path (a.k.a. **Profile Path**) by manually typing* `chrome://version` *on your chrome search bar*

The above is mandatory since the <a href="https://github.com/noahverner1995/Binance-Futures-Trading-Strategies/blob/main/Data%20gathering/data_downloader/automated_data_downloader_for_binance_futures.py">automated_data_downloader_for_binance_futures.py</a> program will use `Selenium` to take control of your browser to automate the download of zip files that contain the desired OHLC price data.
