"""Verify the unequal-population example and the one-round-delay threshold."""
import json
import math


def residual(x, alpha, w=.2, beta=5):
    p=1/(1+math.exp(-(math.log(w/(1-w))+2*beta*(x-w))))
    return (1-alpha)*p+alpha*w-x


def roots(alpha):
    out=[]
    grid=[i/10000 for i in range(10001)]
    for l,r in zip(grid,grid[1:]):
        fl,fr=residual(l,alpha),residual(r,alpha)
        if abs(fl)<1e-13:
            root=l
        elif fl*fr<0:
            for _ in range(45):
                mid=(l+r)/2
                if residual(l,alpha)*residual(mid,alpha)<=0:r=mid
                else:l=mid
            root=(l+r)/2
        else: continue
        if not out or abs(out[-1]-root)>1e-5:out.append(root)
    return out


def main():
    result={str(a):roots(a) for a in (.4,.5,.7)}
    assert len(result['0.5'])==3 and len(result['0.7'])==1
    for lam in (.1,.35,1):
        for gamma in (.25,.75,1.25,2.5):
            disc=math.sqrt((1-lam)**2+4*lam*gamma)
            rr=[((1-lam)+disc)/2,((1-lam)-disc)/2]
            assert (max(map(abs,rr))<1)==(gamma<1)
    print(json.dumps(result,indent=2))
    print('PASS: roots and strict delayed stability threshold.')


if __name__=='__main__': main()
