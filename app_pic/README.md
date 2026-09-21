# 商店截圖

- `ios_app_store/`：App Store 6.9、6.7、6.5 吋直式尺寸，每種 4 張。
- `google_play/`：Google Play 1080 × 2160 直式尺寸，共 4 張。
- `marketing_intro/`：兩款商店行銷介紹圖，各含 iOS 6.9、6.5 吋與 Google Play 版本。
- `ios_upload_1284x2778/`：可直接上傳目前 App Store iPhone 欄位的 6 張圖，全部為 1284 × 2778。
- `Screenshot_*_clean_1080x2140.png`：移除 Android 系統列後的乾淨母檔。

原始截圖不會被覆寫。重新產生時執行：

```sh
python3 app_pic/prepare_store_screenshots.py
python3 app_pic/generate_marketing_images.py
```

第一張原始截圖含測試廣告，輸出時會以符合既有介面風格的資訊面板完整覆蓋；正式上架前，仍建議從 app 關閉測試廣告後重新截圖。
