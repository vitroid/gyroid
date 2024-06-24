Gyroid grapheneを自分で作ってみる。

p構造とn構造を考える。

pとはpacking構造のこと。球体のつめあわせでできる構造。二次元平面の場合には最密充填構造は三角格子になる。

nとはネットワーク構造のこと。一定の長さの辺でつながった点でできた、グラフ構造。

1, 曲面に対して、できるだけ密に球をしきつめたp構造を作る。
2. 球は曲面を三角形で埋めつくす。
3. 多くの球は6配位だが、曲率に応じて少数の5配位や7配位の球も生じる
4. 2で作った三角形の中心に新たに頂点を置き、隣接する三角形の中心同士をつなぐ。
5. 結果として生じるグラフはすべての頂点が3配位で、5〜7員環でできたグラフェン状構造になっている。

* 1.の構造を作る際には、粒子間には斥力を働かせ、かつジャイロイド面からずれるとエネルギーが高くなるような外場を加える。
* そして、QuenchとAnnealを併用して、できるだけ粒子が均一に分布するように最適化する。
* 三角形だけで埋めつくせれば問題ないのだが、稀に四角形や五角形が残ってしまう。
  * 前者については、短い方の対角線を強制的につなぐことで三角形にする。
  * 後者については、中心に原子を追加して5つの三角形に置きかえる。
* こうして、完全に三角形だけの近似多面体ができる。
* これの双対を作る。つまり、三角形の中心に頂点を置き、隣接する三角形の中心同士を辺でつないだ別のグラフを構成する。
* すべての三角形は3つの三角形と隣接しているので、双対グラフは3配位となる。また、三角形が正三角形に近いほど、双対グラフの辺の長さが均質化する。

陰関数で表せないような面、例えば多面体なんかに貼りつけるにはどうしたらいい?
その場合も、多面体と点の間の距離を計算できれば、それで場を作れる。
でもどうやって? 既製品があるといいな。
むしろグリッドで与えるほうが簡単かも。そうしよう。


## 2024-06-24

ほぼできた。
* 斥力ポテンシャルには特徴的な長さがないので、箱の大きさにかかわらず自動的に粒子間隔を均質化してくれるのは良いのだが、法線方向への変位に対する外場ポテンシャルとのスケールあわせがてきとうになってしまう。
* Temperingで粒子位置を微調整する場合の温度やdtなんかも、結局斥力の大きさに影響をうける。
* そして窮屈さは粒子数にも依存する。
* どうしたらいい? 設定するパラメータがいくつもあるが、本来は原子数(と斥力の次数)以外はユーザーが気にする必要のない情報。ソフトウェアがよきにはからえばいい。
* Quench前に、まず粒子間力と法線力の比率は指定したい。
* Temperingに進むまえに、温度とdtは最適に設定できると思う。