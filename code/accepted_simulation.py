"""Analytical and finite-feedback checks; no trained model or human data."""
import argparse
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def step(x, beta, alpha, lam, w=.5):
    p = 1/(1+np.exp(-(np.log(w/(1-w))+2*beta*(x-w))))
    return (1-lam)*x+lam*((1-alpha)*p+alpha*w)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    plt.rcParams.update({'font.size':9,'font.family':'DejaVu Sans','pdf.fonttype':42,
                         'axes.spines.top':False,'axes.spines.right':False})
    # Entire-domain convergence, including the nonhyperbolic equality case.
    for lam in (.1,.35,1):
        x = np.linspace(.001,.999,199)
        for _ in range(2000):
            xn = step(x,5,.6,lam)
            assert np.all(np.abs(xn-.5) <= np.abs(x-.5)+1e-15)
            x = xn
        assert np.max(np.abs(x-.5)) < .025
    fig, ax = plt.subplots(1,2,figsize=(7.2,2.8))
    for x0,c in [(.48,'#2963A4'),(.52,'#B7483A')]:
        for a,ls in [(0,'-'),(.7,'--')]:
            hist=[x0]
            for _ in range(65): hist.append(float(step(hist[-1],5,a,.35)))
            ax[0].plot(hist,ls,color=c,label=f'x0={x0}, alpha={a}')
    ax[0].axhline(.5,color='gray',lw=.6)
    ax[0].set(xlabel='Update round',ylabel='Group 1 policy share',ylim=(0,1),title='An audit floor changes the attractor')
    ax[0].legend(frameon=False,fontsize=7)
    alphas=np.linspace(0,1,301)
    lo=np.full_like(alphas,.01); hi=1-lo
    for _ in range(4000):
        lo=step(lo,5,alphas,.35);hi=step(hi,5,alphas,.35)
    ax[1].plot(alphas,hi,color='#B7483A');ax[1].plot(alphas,lo,color='#2963A4')
    ax[1].plot([0,.6],[.5,.5],':',color='gray',label='Unstable representative point')
    ax[1].axvline(.6,color='gray',lw=.7)
    ax[1].set(xlabel='Representative feedback weight alpha',ylabel='Long-run policy share',title='Audit threshold at beta=5')
    ax[1].legend(frameon=False,fontsize=7)
    fig.tight_layout();fig.savefig(args.output_dir/'participation_phase.pdf');plt.close(fig)
    rng=np.random.default_rng(20260904)
    rows=[];samples={}
    reps=2000;rounds=1500;n=m=500;beta=5;lam=.35
    for alpha in (0,.4,.6,.7,.9,1):
        x=np.full(reps,.5)
        for _ in range(rounds):
            p=1/(1+np.exp(-beta*(2*x-1)))
            endogenous=rng.binomial(n,p)/n
            panel=rng.binomial(m,.5,size=reps)/m
            x=(1-lam)*x+lam*((1-alpha)*endogenous+alpha*panel)
        d=1-lam+lam*(1-alpha)*beta/2
        pred=lam**2*((1-alpha)**2/(4*n)+alpha**2/(4*m))/(1-d*d) if d<1 else None
        bias=np.abs(x-.5)
        rows.append({'alpha':alpha,'mean':float(x.mean()),'mean_abs_deviation':float(bias.mean()),
                     'se_abs_deviation':float(bias.std(ddof=1)/np.sqrt(reps)),
                     'variance':float(x.var(ddof=1)),'linear_variance':pred,
                     'large_deviation_rate':float(np.mean(bias>.1))})
        samples[alpha]=x
    fig,ax=plt.subplots(1,2,figsize=(7.2,2.8))
    for a,c in [(.4,'#B7483A'),(.6,'#8B62A6'),(.7,'#23826A')]:
        ax[0].hist(samples[a],bins=np.linspace(0,1,61),histtype='step',density=True,label=f'alpha={a}',color=c)
    ax[0].set(xlabel='Endpoint policy share',ylabel='Density',title='A balanced mean can hide lock-in')
    ax[0].legend(frameon=False,fontsize=8)
    stable=[r for r in rows if r['linear_variance'] is not None]
    ax[1].plot([r['alpha'] for r in stable],[r['variance'] for r in stable],'o-',label='Simulation')
    ax[1].plot([r['alpha'] for r in stable],[r['linear_variance'] for r in stable],'x--',label='Local linear approximation')
    ax[1].set(xlabel='Representative feedback weight alpha',ylabel='Across-replicate variance',title='Noise persists in the stable regime')
    ax[1].ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax[1].legend(frameon=False,fontsize=7)
    fig.tight_layout();fig.savefig(args.output_dir/'participation_noise.pdf');plt.close(fig)
    record={'seed':20260904,'replicates':reps,'rounds':rounds,'n':n,'m':m,'beta':beta,'lambda':lam,'rows':rows}
    (args.output_dir/'simulation.json').write_text(json.dumps(record,indent=2)+'\n')
    for r in rows: print(r)
    print('PASS: equality-case monotonic convergence and finite-feedback simulations.')


if __name__ == '__main__':
    main()
