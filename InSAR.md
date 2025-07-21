# InSAR Workflow Overview

This document outlines the standard workflow for InSAR (Interferometric Synthetic Aperture Radar) processing as implemented in `edk-sar`. Each step is modular and can be adapted to different SAR sensors (e.g., Sentinel-1, ALOS-2, NISAR).

---

## 1. SAR Data Ingestion

Ingest and manage SAR image pairs or stacks for further processing.

---

## 2. Coregistration

Align SAR image pairs at the pixel level to ensure accurate interferogram generation.

---

## 3. Interferogram Generation

Compute phase differences between coregistered SAR images to generate interferograms.

---

## 4. Coherence Estimation

Calculate coherence maps to assess the quality of the interferogram.

---

## 5. Phase Unwrapping

Convert wrapped phase values to continuous phase maps.

---

## 6. Correction Application

Apply atmospheric and orbital corrections to remove artifacts and improve accuracy.

---

## 7. Final Product Generation

Produce final deformation or elevation products in standard GIS formats.

---

## 8. Polarimetric Data Utilization

Leverage polarimetric SAR data (e.g., VV, VH from Sentinel-1; HH, HV from NISAR) to generate additional products such as dual-pol indices for ready-use.

---



### Implementation Steps: 
1. edk_sar.init() -- Launches ISCE2 container
2. edk_sar.workflows.scan() -- Scans for SLCs from ASF data facility, takes bbox and timebounds as inputs
3. edk_sar.workflows.sync() -- Syncs SLCs to local directory
4. edk_sar.workflows.coregister.run() -- Coregisters SLCs, takes bbox and timebounds as input
5. edk_sar.workflows.geocoded() -- Geocodes SLCs, using Geolocation Arrays