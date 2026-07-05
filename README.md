# ITR2 简体中文本地化工作区

![11](https://github.com/jojuniori/ITR2_CN_Localization/raw/main/screenshot/11.png)

本项目工作流含Agent参与。

如需自定义用Agent执行相关内容，我已将相关翻译约束写好，可将之加入到您惯用的Agent的Rule限制当中如：

```markdown
## 翻译规范

详见 [notes/translation_guidelines.md](notes/translation_guidelines.md)。
```

## 当前流程

本工作区以新版 `EnglishSource.uasset` 为唯一源表。

构建流程：

1. 从 `notes/english_source_current_probe.csv` 读取当前游戏真实英文源文本。
2. 生成/刷新 `translation/ITR2_CN_master.csv`。
3. 对每条源文本重新计算 Unreal `StrCrc32` source hash。
4. 从 master CSV 生成 `Localization/Game/en/Game.locres`。
5. 额外补入蓝图中出现但 EnglishSource 未收录的 key。
6. 打包 pak，并生成 Vortex/Nexus 可用 zip 到 `dist/`。

## 主要文件

- `translation/ITR2_CN_master.csv`：唯一权威翻译主表。优先编辑这里。
- `build/reports/ITR2_CN_built_locres_audit.csv`：最近一次构建后的中文 locres 反读核对表；它不是游戏原版 locres。
- `notes/english_source_current_probe.csv`：当前新版 EnglishSource 导出的英文源表。
- `notes/original_current_locres_probe.csv`：当前游戏原版 locres 导出，仅作参考；它和构建后的中文 locres 不应长得一样。
- `dist/`：发布用 zip 输出目录。
- `VERSION`：下一次默认构建要使用的发布版本号；默认构建成功后会自动递增。

## 重新构建

```powershell
pwsh.exe -NoLogo -NoProfile -File .\scripts\build_chs_pak.ps1
```

默认输出：

- `build/z_IntoTheRadius2_SimplifiedChinese_Localization_P.pak`
- `dist/IntoTheRadius2_SimplifiedChinese_Localization_<VERSION>.zip`

不传 `-Version` 时，脚本会读取 `VERSION` 文件作为本次 zip 版本号；构建成功后自动把 `VERSION` 加 `0.0.1`。进位规则为 `v0.3.9 -> v0.4.0`，`v0.9.9 -> v1.0.0`。

指定版本号：

```powershell
pwsh.exe -NoLogo -NoProfile -File .\scripts\build_chs_pak.ps1 -Version v0.3.1
```

手动指定 `-Version` 只影响本次输出，不会推进 `VERSION` 文件。

## CSV 维护

优先修改 `translation/ITR2_CN_master.csv` 的 `new_translation` 列。

主表列顺序：

```text
text, new_translation, notes, key, source_hash, row_no, category, source
```

游戏实际写入使用 `new_translation`。

`build/reports/ITR2_CN_built_locres_audit.csv` 会接近 master 的 `new_translation`，因为它是从刚生成的中文 locres 反读出来的结果。若要查看游戏原版 locres，请看 `notes/original_current_locres_probe.csv`。

## 安装

手动安装：把 dist zip 里的 `.pak` 放到：

```text
IntoTheRadius2\Content\Paks\
```

Vortex 安装：上传/导入 dist zip 即可。zip 根目录包含 pak 文件和 `LICENSES/MapleMono-OFL.txt` 字体许可证。

## 已知问题 (Known Issues)

1. 游戏当前版本将 IZh-27 6发弹带的左右标记放反了，本汉化包已在翻译文本中对调以匹配游戏实际显示。若后续官方修复此问题，弹带名称可能出现左右错位，届时将发布更新。
2. 主流程中还剩2个地方我没法覆盖翻译后的文本，暂时搞不定，不过不影响游玩：
   ![untransed](https://github.com/jojuniori/ITR2_CN_Localization/raw/main/screenshot/untransed.png)

## 免费与版权声明 (Free & License Disclaimer)

1. **完全免费 (100% Free)**：本 Mod 为个人/社区自发的非营利汉化作品，**完全免费发布**。
2. **严禁商用 (Non-Commercial Only)**：本 Mod 采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans) 许可协议授权。**严禁任何人或组织将本 Mod 及其衍生修改版用于任何形式的商业用途（包括但不限于电商倒卖、打包收费、付费下载、挂靠打赏/广告、作为收费会员专属福利等）**。
3. **谨防受骗 (Consumer Warning)**：如果您在任何第三方平台（如淘宝、闲鱼、拼多多等）上付费购买了本 Mod，说明您已被骗！请立即向平台申请退款并举报盗卖商家。本团队将对一切未经授权的商业盗卖行为发起平台侵权下架申诉（IPP/DMCA）。

## 截图 (Screenshots)

![12](https://github.com/jojuniori/ITR2_CN_Localization/raw/main/screenshot/12.png)
![13](https://github.com/jojuniori/ITR2_CN_Localization/raw/main/screenshot/13.png)
![14](https://github.com/jojuniori/ITR2_CN_Localization/raw/main/screenshot/14.png)
![15](https://github.com/jojuniori/ITR2_CN_Localization/raw/main/screenshot/15.png)
![16](https://github.com/jojuniori/ITR2_CN_Localization/raw/main/screenshot/16.png)
![17](https://github.com/jojuniori/ITR2_CN_Localization/raw/main/screenshot/17.png)
![22](https://github.com/jojuniori/ITR2_CN_Localization/raw/main/screenshot/22.png)
![23](https://github.com/jojuniori/ITR2_CN_Localization/raw/main/screenshot/23.png)
![24](https://github.com/jojuniori/ITR2_CN_Localization/raw/main/screenshot/24.png)
![25](https://github.com/jojuniori/ITR2_CN_Localization/raw/main/screenshot/25.png)
