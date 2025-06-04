# lgmproxies
Proxy data calibration for the LGM
Below we hightlight some results from [notebooks/play.ipynb](notebooks/play.ipynb)

## Tierney et al 2020 LGM paper

![Tierney calibration](images/tierney_calibration.png)


## Proxy-specific results

Below we try to match Tierney et al results. I'll update the figs below as I make progress, dropping irrelevant results to keep the figures clear.

### UK37
![UK37](images/uk37_calibration.png)

### Tex 86
![Tex86](images/tex86_calibration.png)

### $\delta^{18}O$

 After failing to get anything interesting with Gaskell and Hull (2023), I now use pooled bayfox with brews/d18oc_sst for d18O. Caveat: these results use present-day deltaO18 (--> only the late Holocene panel makes sense) ! I also added the hierarchical (species-specific), annual model but the results differ much more from the CSV file provided by Tierney et al.
![$\Delta^{18}O$](images/delo_calibration_overview.png)
See also [species-specific subplots with error bars](images/delo_calibration.png).

Even when using the Malevitch et al (2019) calibration dataset the "reverted" SST results are off with the hierarchical model, whereas the pooled model works both ways.
![reverted](/images/d18o_sst_pooled_vs_hierarchical.png)
![forward](/images/d18o_sst_pooled_vs_hierarchical.png)

The calibration and the last two plots is done in [this notebook](/notebooks/bayesian_calibration_examples.ipynb) adapted from [this companion repo from Malevitch et al](https://github.com/brews/d18oc_sst). The re-use as "reverted" model is done [here](/lgmproxies/datasets/tierney.py). That's the most likely place to search for any issue, but I failed to see any.

### Mg / Ca
![Mg / Ca](images/mg_calibration.png)

## Sea-water $\delta^{18}O$

There is a tool (Gaskell and Hull 2023):
- github: https://github.com/danielgaskell/d18Oconverter
- tool: https://research.peabody.yale.edu/d180/index.html
- paper: https://cp.copernicus.org/articles/19/1265/2023

That claims to take latitude + age as input and return delta O 18
But unless I'm mistaken, the results are pretty different from (probably correct) Malevich et al (2019):

- github: https://github.com/brews/d18oc_sst
- paper: https://doi.org/10.1029/2019pa003576

despite the claim they also based their calculation on Malevitch et al. Perhaps I did something wrong...

![](images/d18osw_comparison.png)
![](images/d18osw_comparison_scatter.png)

At least the resulting temperature is correlated.

## External resources:

- [Chat GPT overview](https://chatgpt.com/share/682f9b2c-ab58-8008-9a48-dbffbbdbf2e9)
- [notebooks history](http://134.1.7.52/albedo/lgmproxies/html)
- [LGMDataAssim repo](https://github.com/awi-esc/LGMDataAssim)
- [LGMDataAssimPaper repo](https://github.com/awi-esc/LGMDataAssimPaper)