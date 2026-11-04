<p>
  <img src="./assets/mlse-banner.jpeg">
</p>

# SPL Open Data
The SPL Open Data repository acts as a collection of biomechanics datasets collected by Maple Leaf Sports & Entertainment's (MLSE) Sport Performance Lab (SPL) in Toronto, Ontario, Canada. Through the open-sourcing of this data, SPL's goal is to provide raw markerless motion capture data typically used by sports biomechanists to the general public in an effort to improve data equity and analytical biomechanical skills in the community.

## Quick Start

Clone this repository using:

```
git clone https://github.com/mlsedigital/SPL-Open-Data.git
```

## File Structure

Assuming that you have cloned the repository, the naming convention of the files is as follows. The data in this repository is structured in the following tree:

```
[sport]/
├─ [action_type]/
│  ├─ participant_information.json
│  ├─ [participant_id]/
│  │  ├─ trial_data/
|  |     ├─ [trial_id].json
```

where, trial data is unique to each individual participant and anonymized, demographic information relating to all participants is referenced in the `participant_information.json` file.

## Data summary

*Last updated: November 2026*

Each "Action" will typically feature a corresponding README file, with relevant documentation.

<center>

| Sport | Action | Participants (total) | Trials (total) | Sessions (total)
| :-: | :-: | :-: | :-: | :-:
| Basketball | [FT](./basketball/freethrow/) | 5 | 583 | 2
| Hockey | [Save](./hockey/goalie/) | 1 | 81 | 1

</center>

## License

License
CC BY-NC-SA 4.0

Attribution-NonCommercial-ShareAlike 4.0 International

https://creativecommons.org/licenses/by-nc-sa/4.0/

Detailed information can be found in LICENSE.

# Data Collection & Participant Release
The datasets in this repository have been collected using SPL's internal biomechanics technology and the participants within them are non-professional athletes having given fully informed consent for the release of their movement capture data.

# Inspirations
This package is inspired by Driveline Baseball's [OpenBiomechanics Project](https://github.com/drivelineresearch/openbiomechanics), one of the largest collections of open-source baseball and high performance biomechanics datasets, and with these datasets, we hope to also inspire the future release of biomechanical data from other organizations.
