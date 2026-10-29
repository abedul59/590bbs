# MacroWave 全方位更新中心

單一 GUI 與單一 Windows EXE，整合以下四個既有 Python 工具：

- MacroWave／Mark 17
- 六大指標與本益比區間
- 台股資金流向
- Bengo 大戶籌碼

## 使用方式

1. 執行 `MacroWave_AllInOne.exe`。
2. 在「設定」填入 FRED API Key、共同股票清單及等待秒數並儲存。
3. 回到「一鍵更新」，勾選工作後按「一鍵更新全部」。
4. 每個工作獨立執行；單一工作失敗不會阻止後續工作。

設定、JSON 備份與 `AllInOne_Logs` 都會保存在 EXE 所在資料夾。

需要安裝最新版 Google Chrome；Selenium Manager／webdriver-manager 會配對 ChromeDriver。
