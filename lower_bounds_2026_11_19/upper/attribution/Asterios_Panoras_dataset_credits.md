# Squares in Squares - Best Packings (22.13193)

* `submission.csv` - 500,500 rows (`id,n,square_id,x,y,angle`), ready to submit.
* `per_n_L.csv` - `n, L, score_n` (score_n = L/sqrt(n) - 1).

Score (official metric code): **22.131928256539**.

## Credit
Areeb Ali (The Last 1e-9: his newest certified packings were merged shortest-per-n).
Ross Wade (Jammed Squares: Contact Forces and Fast LP Search; his jammed-squares-engine-packings dataset and the Hopper search, re-run locally with more compute for n=645).
Also: Penguin (Public Changed Grain Certified Union), Areeb Ali (Merge 28, Certify, Shrink; his engine was used for the certified micro-shrink), Sigmaborov (Certified Contact Polish), Nilanjan Saha and jazivxt (newest merges).

Merged from public work: Alex Chilton (Squares in Squares starter kit dataset: new packings for n=330 and n=367), the base is the best shortest-per-n merge of the newest public outputs: Penguin (Whole Packing Warp Pilot, Learned Birth Chains Pilot, Public Neural Recovery Union, Recovered Grain Union, GA Contact and Chilton82 certified unions), Nilanjan Saha (Certified Portfolio Merge + Proj Quench, Certified Merge + Projection Quench + GPU Screen), Sung Heo / kmmmvs (Public Merge Daily), Nevska (Explorer), samanyu1808 (sis-submit v2), Areeb Ali (Merge 28, Certify, Shrink), Malyshev Danil (Living Atlas) and jazivxt (Boxed In Sub, 22.1370055). These themselves merge the work of many authors (lucifer19 Think. Select. Reclose, Malyshev Danil Living Atlas, Alex Chilton fault-line DP and starter kit, avazaku, Chris Deotte, Kirill Tymchishin, Penguin, Nilanjan Saha, Busya PRIME and others), built on Evan Daniel's and Francisco Couzo's MIT-licensed tools and the Soft-to-Rigid engine by Yohei Nakajima. Own contribution: basin hopping with Evan Daniel's packer driven by Alex Chilton's hop_search script, each result certified with the competition metric (n=585, 632 and 914 are clearly ours; 747, 748, 749 and 804 are ours by a hair; n=492, 803, 851, 910, 911 were since matched or beaten by public work). The whole file was checked with the official metric code (22.134373451549, no rejected puzzle).
