# How To Correctly Use The automated_data_downloader_for_binance_futures.py

After running a Chrome session following <a href="https://github.com/noahverner1995/Binance-Futures-Trading-Strategies/blob/main/Data%20gathering/README.md"> the previous procedure</a>
you will have to change manually the default download directory to another one in which you desire to store the zip files that contain the desired OHLC price data.

To do so, first read <a href="https://www.guidingtech.com/change-download-location-in-google-chrome/">this guide</a>, and do what it says, make sure to have chosen an empty folder to store the files.

Then, before running the `automated_data_downloader_for_binance_futures.py` program, you will have to modifiy the following lines:

* Line 17: change your_chromedriver.exe_path for literally your chromedriver.exe path, keep it inside the r'' btw.
* Line 22: change https://data.binance.vision/?prefix=data/futures/um/daily/markPriceKlines/XRPUSDT/1h/ for your desired pair with its respective timeframe.

*Note: You can get any markPriceklines for any available futures pair at https://data.binance.vision/?prefix=data/futures/um/daily/markPriceKlines/*
