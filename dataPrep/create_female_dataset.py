"""
Consolidate all dataset clips into a single `female` directory with
22050 Hz wav files and matching .lab transcripts.

Usage:
    python create_female_dataset.py \
        --dataset-root /Users/derekvawdrey/Workspace/School/CS479FinalProject/dataPrep/dataset \
        --target-sr 22050
"""

import argparse
import sys
from pathlib import Path
from typing import Dict

import torch
import torchaudio


def load_transcripts(transcript_path: Path) -> Dict[str, str]:
    """Return {clip_id: transcript} for a dataset transcript file."""
    mapping: Dict[str, str] = {}
    if not transcript_path.is_file():
        return mapping

    with transcript_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key = None
            text = ""
            if ":" in line:
                key, text = line.split(":", 1)
            elif "\t" in line:
                key, text = line.split("\t", 1)
            else:
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    key, text = parts
            if key:
                mapping[key.strip()] = text.strip()
    return mapping


def ensure_mono(waveform: torch.Tensor) -> torch.Tensor:
    """Collapse multi-channel audio to mono (torchaudio expects [channels, time])."""
    if waveform.ndim != 2:
        raise ValueError("Expected waveform with shape [channels, time]")
    if waveform.size(0) == 1:
        return waveform
    return waveform.mean(dim=0, keepdim=True)


def resample_if_needed(
    waveform: torch.Tensor, orig_sr: int, target_sr: int
) -> torch.Tensor:
    """Resample waveform if sample rate differs."""
    if orig_sr == target_sr:
        return waveform
    return torchaudio.functional.resample(waveform, orig_sr, target_sr)


def convert_dataset(
    dataset_root: Path, output_root: Path, target_sr: int, overwrite: bool
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    dataset_dirs = sorted(
        d for d in dataset_root.iterdir() if d.is_dir() and d.name != output_root.name
    )
    if not dataset_dirs:
        print(f"No datasets found in {dataset_root}")
        return

    for dataset_dir in dataset_dirs:
        wav_dir = dataset_dir / "wav"
        transcript_file = dataset_dir / "transcript_utf8.txt"

        if not wav_dir.is_dir():
            print(f"⚠️ Skipping {dataset_dir.name}: missing wav directory")
            continue

        transcripts = load_transcripts(transcript_file)
        if not transcripts:
            print(f"⚠️ Skipping {dataset_dir.name}: no transcripts loaded")
            continue

        wav_paths = sorted(wav_dir.glob("*.wav"))
        if not wav_paths:
            print(f"⚠️ Skipping {dataset_dir.name}: no wav files found")
            continue

        print(f"Processing {dataset_dir.name} ({len(wav_paths)} files)")
        for wav_path in wav_paths:
            clip_id = wav_path.stem
            transcript = transcripts.get(clip_id)
            if not transcript:
                print(f"  ⚠️ Missing transcript for {clip_id}, skipping")
                continue

            output_wav = output_root / f"{clip_id}.wav"
            output_lab = output_root / f"{clip_id}.lab"

            if not overwrite and output_wav.exists() and output_lab.exists():
                continue

            waveform, sample_rate = torchaudio.load(str(wav_path))
            waveform = ensure_mono(waveform)
            waveform = resample_if_needed(waveform, sample_rate, target_sr)

            torchaudio.save(str(output_wav), waveform, target_sr)
            output_lab.write_text(transcript + "\n", encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create consolidated female dataset with 22050 Hz wav and .lab files."
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path(__file__).resolve().parent / "dataset",
        help="Root directory containing dataset subfolders (default: dataPrep/dataset).",
    )
    parser.add_argument(
        "--output-name",
        type=str,
        default="female",
        help="Name of the consolidated output directory (default: female).",
    )
    parser.add_argument(
        "--target-sr",
        type=int,
        default=22050,
        help="Target sample rate for converted wav files (default: 22050).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing wav/lab files (default: skip existing).",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> None:
    args = parse_args(argv)
    dataset_root: Path = args.dataset_root
    output_root = dataset_root / args.output_name
    convert_dataset(dataset_root, output_root, args.target_sr, args.overwrite)


if __name__ == "__main__":
    main(sys.argv[1:])


