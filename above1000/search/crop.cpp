#include <cstdio>
#include <cmath>
#include <vector>
#include <algorithm>
#include <cstdlib>
using namespace std;
const int M=33,E=48;const double tol=1e-7;
struct Pt{double x,y,t;};
struct Edge{double f;int usable;};
struct Best{double f=1.;int s=-1,id,ox,oy;};
Best best[2][M][M][E];
void scan(const vector<Pt>& p,int s,int id,int ox,int oy){
 int base[M][M]={},mxx=0,mxy=0;
 vector<Edge> ev[M][M];
 for(auto q:p){
  double h=(fabs(cos(q.t))+fabs(sin(q.t)))/2;
  if(q.x-h < ox-tol || q.y-h < oy-tol)continue;
  double x=q.x+h-ox,y=q.y+h-oy;
  int a=floor(x-tol),b=floor(y-tol);
  if(a<0||b<0||a>=M||b>=M)continue;
  mxx=max(mxx,a+1);mxy=max(mxy,b+1);
  if(a+1<M && b+1<M) base[a+1][b+1]++;
  auto add=[&](int A,int B){
   double f=max({0.,x-A,y-B});
   if(f>=1.-tol)return;
   bool clear=(x<=A+tol||y<=B+tol);
   if(!clear){
    double c=cos(q.t),ss=sin(q.t);
    // Distance along either tilted square axis, between centers of a unit square and the corner cutout.
    double dx=A+f/2-(q.x-ox),dy=B+f/2-(q.y-oy),rr=.5+f*h;
    clear=(fabs(dx*c+dy*ss)>=rr-tol || fabs(dx*ss-dy*c)>=rr-tol);
   }
   ev[A][B].push_back({f,clear?1:0});
  };
  for(int b2=b;b2<M;b2++)add(a,b2);
  for(int a2=a+1;a2<M;a2++)add(a2,b);
 }
 for(int a=0;a<min(M,mxx);a++)for(int b=0;b<min(M,mxy);b++){
  int &v=base[a][b]; v+=(a?base[a-1][b]:0)+(b?base[a][b-1]:0)-(a&&b?base[a-1][b-1]:0);
  auto &es=ev[a][b]; if(es.empty())continue;
  sort(es.begin(),es.end(),[](Edge x,Edge y){return x.f<y.f;});
  int counts[2]={v-a*b,v-a*b};
  for(auto e:es){
   for(int z=0;z<=e.usable;z++){
    int ex=++counts[z]; if(ex<=0||ex>=E)continue;
    auto &r=best[z][a][b][ex]; if(e.f<r.f-1e-12){r={e.f,s,id,ox,oy};}
   }
  }
 }
}
int main(int argc,char**argv){
 FILE *f=fopen("geom.bin","rb"); if(!f) return 2;int n,inner=argc>1?atoi(argv[1]):0,offs=argc>2?atoi(argv[2]):0;
 for(int s=0;fread(&n,4,1,f);s++){
  vector<Pt> p(n);if(fread(p.data(),sizeof(Pt),n,f)!=(size_t)n)return 1;
  double xl=1e9,yl=1e9,xh=-1e9,yh=-1e9;bool tilt=false;
  for(auto q:p){double h=(fabs(cos(q.t))+fabs(sin(q.t)))/2;xl=min(xl,q.x-h);yl=min(yl,q.y-h);xh=max(xh,q.x+h);yh=max(yh,q.y+h);if(h>.505)tilt=true;}
  if(!tilt)continue;
  for(int id=0;id<4;id++){
   auto v=p; for(auto &q:v){q.x=(id&1)?xh-q.x:q.x-xl;q.y=(id&2)?yh-q.y:q.y-yl;if(id==1||id==2)q.t=-q.t;}
   for(int i=offs;i<=inner;i++)for(int j=offs;j<=inner;j++)scan(v,s,id,i,j);
  }
 }
 for(int z=0;z<2;z++)for(int a=1;a<M;a++)for(int b=1;b<M;b++)for(int e=1;e<E;e++){auto v=best[z][a][b][e];if(v.s>=0)printf("%d %d %d %d %.14f %d %d %d %d\n",z,a,b,e,v.f,v.s,v.id,v.ox,v.oy);}
}
