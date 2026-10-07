# Taiwan Explorer WordPress 版本

這套檔案是從目前的 `index.html` 分離出來的 WordPress 版本，不使用 iframe。

## 使用方式

1. 將 `wordpress-index.html` 全部貼到 WordPress 的「自訂 HTML」區塊。
2. 將 `wordpress-index.css` 貼到「外觀 → 自訂 → 額外 CSS」，或 Custom CSS & JS 外掛的 CSS 欄位。
3. 將 `wordpress-index.js` 貼到 Custom CSS & JS 外掛的 JavaScript 欄位。

JS 會在主視覺圖片載入後啟用呼吸燈效果，並尊重使用者的「減少動態」設定。
