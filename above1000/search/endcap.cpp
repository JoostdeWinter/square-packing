#include <bits/stdc++.h>
using namespace std;
const int OF=400,BM=35,KM=101,EM=800;
struct Band{short b,p,R,l,r; double d=-1;};
struct Pair{Band v,h;double d=-1;int cap=0,k=0;};
int main(int argc,char**argv){
 int km=atoi(argv[1]),bm=atoi(argv[2]),den=atoi(argv[3]),step=atoi(argv[4]);
 static Band vert[KM][BM][EM],horiz[KM][EM];static Pair sol[10001];
 for(int b=2;b<=bm;b++)for(int p=1;p<den*.50;p+=step){
  double t=p/(double)den,c=(1-t*t)/(1+t*t),s=2*t/(1+t*t),w=b*c+s,delta=b-w;
  if(delta<=0||delta>1.65)continue;
  // Incremental fill of one band end: column m of level i is admissible from this lift.
  vector<double> h;h.push_back(0);
  for(int i=0;i<30;i++){double low=i+1-b*s+s/c;if(low>3.1)break;
    for(int m=1;m<=floor(w+1e-12);m++){double d=max(0.,i+1-b*s+m*s/c);if(d>3.1)break;h.push_back(d);}
  }
  sort(h.begin(),h.end());int M=h.size()-1;
  vector<double> delay(2*M+1,1e8);vector<int> split(2*M+1);
  for(int i=0;i<=M;i++)for(int j=0;j<=i;j++){
   double x=h[i]+h[j];if(x<delay[i+j])delay[i+j]=x,split[i+j]=i;
  }
  for(int k=1;k<=km;k++){
   int Rmax=(int)floor((k-(b*s+c))*c+1e-11)+1;
   for(int R=max(1,Rmax-2);R<=Rmax;R++){
    double base=(R-1)/c+b*s+c,slack=k-base;
    int e=upper_bound(delay.begin(),delay.end(),slack+1e-10)-delay.begin()-1;
    if(e<0)continue;
    int bonus=b*R+e-k*b;
    if(bonus+OF>=0&&bonus+OF<EM){Band &hh=horiz[k][bonus+OF];if(delta>hh.d)hh={short(b),short(p),short(R),short(split[e]),short(e-split[e]),delta};}
    if(k<=b)continue;
    for(;e>=0;e--){int ex=b*R+e-k*b;if(ex+OF<0)break;if(ex+OF>=EM)continue;
     double d=min(delta,k-base-delay[e]);if(d<=0)continue;
     Band &v=vert[k][b][ex+OF];if(d>v.d)v={short(b),short(p),short(R),short(split[e]),short(e-split[e]),d};
     if(d>=delta-1e-12)break;
    }
   }
  }
 }
 for(int k=6;k<=km;k++)for(int b=2;b<k&&b<=bm;b++){
  for(int i=0;i<EM;i++){auto v=vert[k][b][i];if(v.d<0)continue;
   for(int j=0;j<EM;j++){auto h=horiz[k-b][j];if(h.d<0||h.b>=k)continue;
    int n=k*k+i+j-2*OF;if(n<1||n>10000)continue;
    double delta=min(v.d,h.d);
    if(!sol[n].k||k-delta<sol[n].k-sol[n].d)sol[n]={v,h,delta,n,k};
   }
  }
 }
 for(int n=km*km-1;n>=1;n--){if(sol[n+1].k&&(!sol[n].k||sol[n+1].k-sol[n+1].d<sol[n].k-sol[n].d))sol[n]=sol[n+1];}
 cout.precision(14);for(int n=1;n<=km*km;n++){auto a=sol[n];if(!a.k)continue;cout<<n<<' '<<a.k<<' '<<a.k-a.d<<' '<<a.cap;for(auto x:{a.v,a.h})cout<<' '<<x.b<<' '<<x.p<<' '<<den<<' '<<x.R<<' '<<x.l<<' '<<x.r;cout<<'\n';}
}
