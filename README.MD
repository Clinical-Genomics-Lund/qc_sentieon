## Sentieon QC

To be run in folder of Sentieon QC outputs together with dedup metrics from Sentieon dedup.

Ouptuts a json with relevant QC-information to whole-genome sequencing or panels(WES included).

### WGS

#### INPUTS
`qc_sentieon.pl $id wgs > $id.QC`

requires the following parameters from sentieon qc
* --algo MeanQualityByCycle mq_metrics.txt
* --algo QualDistribution qd_metrics.txt
* --algo GCBias --summary gc_summary.txt gc_metrics.txt
* --algo AlignmentStat aln_metrics.txt
* --algo InsertSizeMetricAlgo is_metrics.txt
* --algo WgsMetricsAlgo wgs_metrics.txt

Plus

* --algo Dedup --score_info $scores --metrics dedup_metrics.txt 

#### OUTPUTS
* "ins_size" : "",
* "sd_coverage" : "",
* "dup_reads" : "",
* pct_above_x" : {
  * "80" : "",
  * "20" : "",
  * "5" : "",
  * "10" : "",
  * "15" : "",
  * "25" : "",
  * "40" : "",
  * "60" : "",
  * "30" : "",
  * "1" : "",
  * "90" : "",
  * "50" : "",
  * "70" : "",
  * "100" : ""
* "mapped_reads" : ,
* "num_reads" : "",
* "dup_pct" : "0.",
* "sample_id" : "",
* "mean_coverage" : "",
* "ins_size_dev" : "",
* "median_cov" : ""



### Panels
#### INPUTS
`qc_sentieon.pl $id panel > $id.QC`

--algo MeanQualityByCycle mq_metrics.txt
* --algo QualDistribution qd_metrics.txt
* --algo GCBias --summary gc_summary.txt gc_metrics.txt
* --algo AlignmentStat aln_metrics.txt
* --algo InsertSizeMetricAlgo is_metrics.txt
* --algo HsMetricAlgo --targets_list $target_intervals --baits_list $target_intervals hs_metrics.txt
* --algo CoverageMetrics --cov_thresh 1 --cov_thresh 10 --cov_thresh 30 --cov_thresh 100 --cov_thresh 250 --cov_thresh 500 cov_metrics.txt

Plus

* --algo Dedup --score_info $scores --metrics dedup_metrics.txt

#### OUTPUTS

* "sample_id" : "",
* "fold_enrichment" : "",
* "mapped_reads" : "",
* "mean_cov" : ,
* "pct_on_target" : "",
* "ins_size" : "",
* "median_coverage" : "",
* "ins_size_dev" : "",
* "tot_reads" : "",
* "fold_80" : "",
* "dup_pct" : ,
  * "pct_above_x" : {
  * "1000" : ,
  * "100" : ,
  * "1" : ,
  * "10" : ,
  * "30" : ,
  * "500" : ,
  * "250" : 
* "dup_reads" : ""
