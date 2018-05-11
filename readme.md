# coglust

## Dictionary gathering

In your experiments folder, create a `langs` file with the languages you want. Then gather words from Panlex, compute backtranslations (takes some time), and merge with Wiktionary:

    mkdir dicts
    ~/coglust/createdicts.py
    ~/coglust/gather_from_dicts.py langs gathered --gathered_panlex dicts

## Clustering

Initially cluster using unweighted distance:

    ~/coglust/cluster.py gathered lev 0.4 unweighted-0.4 --linkage single
    mkdir singles
    ~/coglust/clustered2bitext.py unweighted-0.4
    mkdir exp1
    mv train* test* dev* unk* exp1

Create and run jobs. Note the space before --train. Also note that alignment will segfault if bitext is empty.

    ~/multral/run.py $(pwd)/exp1 --flags ' --train'
    qsub train.sh
    ~/coglust/getlexfiles.py exp1


## Citation

*Creating Large-Scale Multilingual Cognate Tables*, Winston Wu and David Yarowsky (2018).
