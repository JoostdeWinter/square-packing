#include <cstdio>
#include <algorithm>
#include <cmath>
#include <vector>
using namespace std;
struct B{int z,a,b,e;double f;int s,id,ox,oy,swap,idx;};
int main(){vector<B> v; B p{};int l=0;
while(scanf("%d%d%d%d%lf%d%d%d%d",&p.z,&p.a,&p.b,&p.e,&p.f,&p.s,&p.id,&p.ox,&p.oy)==9){p.idx=l++;p.swap=0;v.push_back(p);swap(p.a,p.b);p.swap=1;v.push_back(p);}
const int K=100,E=120; static double best[K][E];static int r1[K][E],r2[K][E];for(auto &i:best) for(double &j:i)j=1.;
auto add=[&](int k,int e,int i,int j,double f){if(k<K && e<E&&best[k][e]>f){best[k][e]=f;r1[k][e]=i;r2[k][e]=j;}};
for(int i=0;i<(int)v.size();i++){
 auto &a=v[i];add(max(a.a,a.b),a.e,i,-1,a.f);
 for(int j=0;j<=i;j++){
 auto &b=v[j];int w=a.a+b.a,h=a.b+b.b;
 int k=max(w,h)+(w==h&&!(a.z||b.z));add(k,a.e+b.e,i,j,max(a.f,b.f));
 }
}
for(int k=1;k<K;k++)for(int e=1;e<E;e++){if(k>1&&best[k-1][e]<best[k][e]){best[k][e]=best[k-1][e];r1[k][e]=r1[k-1][e];r2[k][e]=r2[k-1][e];} if(best[k][e]<1)printf("%d,%d,%d,%.14f,%d,%d\n",k,e,k*k+e,k+best[k][e],r1[k][e],r2[k][e]);}
}
