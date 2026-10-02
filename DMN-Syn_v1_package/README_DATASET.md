# DefMoN-Syn v1 (formerly DMN-Syn v1.0)

**Defensive Motivational Node Synthetic Corpus**  
Quadri-lingual (EN/KO/FR/KA) synthetic dataset generated under the **DefMoN** framework.  

This dataset accompanies the paper:  
> Kim, Ryan SangBaek (2025).  
> *DefMoN: A Theory-Grounded Generative Framework and a Multilingual Synthetic Corpus for Inferring Defensive Motivational Nodes in Text*.  
> Zenodo. [https://doi.org/10.5281/zenodo.17112915](https://doi.org/10.5281/zenodo.17112915)

Dataset DOI (Zenodo): [10.5281/zenodo.17101927](https://doi.org/10.5281/zenodo.17101927)

---

## Contents

- `DMN-Syn_v1.csv` – Main dataset (300 rows)  
- `schema.json` – Formal schema (field definitions)  
- `distribution_report.json` – Language, defense, emotion counts  
- `v1_0_1_diff.json` – Notes on minor QC fixes for upcoming v1.0.1  
- `LICENSE-CC-BY-4.0.txt` – License file  

---

## Schema

Each row contains:

| Field       | Type     | Description |
|-------------|----------|-------------|
| `id`        | string   | Unique identifier |
| `language`  | string   | Language code (`en`, `ko`, `fr`, `ka`) |
| `text`      | string   | Synthetic utterance |
| `defense`   | string   | One of 10 defense mechanisms |
| `motivation`| string   | One of 8 Plutchik primary emotions |
| `meta_json` | JSON     | Metadata (template_id, scenario, style, intensity, seed, etc.) |

---

## Distribution

- **Languages**: EN 100, KO 100, FR 50, KA 50  
- **Defenses**: 10 categories (see Table in manuscript, not perfectly balanced)  
- **Motivations**: Full coverage of 8 emotions  

See `distribution_report.json` for detailed counts.

---

## Notes on Duplicates

While **near-duplicate removal (F3)** was applied during generation,  
a small set of **exact duplicates** (~40/300, ≈13%) remains in v1.0.  
These are **intentional**:  
- Same surface text may appear under different (Defense, Emotion) tuples.  
- This design enables **controlled cross-axis evaluation**.  
- They do **not affect** the reported distributions (Tables in the paper).  

This choice is documented in the manifests and will remain for reproducibility.  

---

## License

- **Data**: CC BY 4.0  
- **Code**: MIT  

Please cite the Zenodo DOI and the associated paper if you use this dataset.

---

## Limitations

- v1.0 includes two Korean rows with blank/punctuation-only text.  
  These do not affect reported results and will be repaired in v1.0.1 with an accompanying diff and checksum.  
- Dataset size is small (300 rows) and synthetic; not for diagnostic or screening use.  
- Cross-cultural deployment requires expert review and adaptation.

---

## Citation

### Dataset

```bibtex
@dataset{kim2025defmonsyn,
  author    = {Kim, Ryan SangBaek},
  title     = {DefMoN-Syn v1 (formerly DMN-Syn v1.0)},
  year      = {2025},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.17101927}
}