URL="https://storage.googleapis.com/kaggle-data-sets/30106/38371/bundle/archive.zip?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=gcp-kaggle-com%40kaggle-161607.iam.gserviceaccount.com%2F20240310%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20240310T113823Z&X-Goog-Expires=259200&X-Goog-SignedHeaders=host&X-Goog-Signature=79cb6f629bc9c58b941d2fbc423f7ab0c9476501f90ae1247b275eeca8a2c16d3898dc36eebb078d9deb1148fd39cc462df03f3517232efbad1844d29359ee1453a4abb58651d5f1f50dffd23efd08eaa7e43a1ad6b8d15346b4fa69bbd9804b7fe0629d9b599ac875505b6462a0c77674bca88e7f316ce01d821cd6b43cd12edcbc586c090a6b19ec67c6852642e92c0c2a3d79d782cbeb71e9be3b92fe66ca37a622052cf87f958eda89ad659708fe73cd5325453c2966e28eb07d4179604be11c229c9de702d5c9f4e8f1e5ed90f09e62a1ece942981423eaf4116f548bb76bf431a823355b5481aea2e2574af09975e7e6cef42bd1104e08d41079cbbd4c"
DIR="datasets"
ARCHIVE="${DIR}/archive.zip"

if [ ! -d "$DIR" ]; then
  echo "Create folder ${DIR}..."
  mkdir $DIR
fi

if [ ! -f "$ARCHIVE" ]; then
  echo "Download archive ${DIR}..."
  curl -o $ARCHIVE $URL
  unzip $ARCHIVE -d datasets
fi

FILES="${DIR}/lesmis/*.wav
${DIR}/lupincontresholme/*.wav
"
for f in $FILES
do
	echo "Processing $f"
  path=$(dirname "$f")
  filename=$(basename "$f")
	sox "$f" -r 16000 -c 1 -b 16 "$path/16k_$filename"
done



