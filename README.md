# European Electricity Carbon Intensity & Renewable Growth (15-Year Analysis)

## Project Overview
This repository contains my final capstone project analyzing how the growth of wind and solar power 
has impacted electricity carbon intensity gCO2/kWh across Europe over the last 15 years. 
Using Python and interactive Bokeh visualizations, this project explores why certain European nations 
reduce carbon emissions faster than others when they show a similar percentage of wind and solar generation.

## Research Question
> **How has the growth of wind and solar power changed electricity carbon intensity
> in Europe over the last 15 years, and which countries give the best example for reducing emissions?**

## Data Source
* **Ember Dataset(`release_generation_yearly_lower.csv`):** [Ember Yearly Electricity Data](https://ember-energy.org) — comprehensive annual data on global electricity generation and carbon intensity.
* **Energy Dataset (`owid-energy-data.csv`):** [Our World in Data – Energy Dataset](https://github.com) containing yearly shares of solar, wind, hydro, and coal energy across countries.
* **CO2 Emissions Dataset (`owid-co2-data.csv`):** [Our World in Data – CO2 and Greenhouse Gas Emissions Dataset](https://github.com) containing total CO2 emissions and per capita emissions by country and year.

## Repository Structure
* `datasets/` Datasets from Ember and OWID.
* `capstone.py`  Python scripts used for data processing and generating Bokeh visualizations.
