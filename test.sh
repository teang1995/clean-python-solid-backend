http -v POST localhost:5000/sign-up name=임용택1 email=teang19951@ajou.ac.kr
echo "First user signed in."
sleep 1

http -v POST localhost:5000/sign-up name=임용택2 email=teang19952@ajou.ac.kr
echo "Second user signed in."
sleep 1

http -v POST localhost:5000/sign-up name=임용택3 email=teang19953@ajou.ac.kr
echo "Third user signed in."
sleep 1

http -v POST localhost:5000/sign-up name=임용택4 email=teang19954@ajou.ac.kr
echo "Fourth user signed in."
sleep 1

http -v POST localhost:5000/tweet id:=1 tweet="My First Tweet" 
echo "user1 tweeted."
sleep 1

http -v POST localhost:5000/tweet id:=5 tweet="My First Tweet -> will raise error"
echo "user5 tried to tweet, but user5 not exists so it raise error."
sleep 1

http -v POST localhost:5000/follow id:=1 follow:=2
echo "user1 followed user2"
sleep 1

http -v POST localhost:5000/follow id:=1 follow:=5
echo "user1 followed user5 but user5 not exists so it raise error."
sleep 1

http -v POST localhost:5000/follow id:=5 follow:=1
echo "user5 tried to unfollow user1 but user5 not exists so it raise error."
sleep 1

http -v POST localhost:5000/follow id:=1 follow:=5
echo "user1 tried to unfollow user5 but user5 not exists so it raise error."
sleep 1

http -v POST localhost:5000/unfollow id:=1 unfollow:=2
echo "user1 unfollowed user2."
sleep 1

http -v GET localhost:5000/timeline/1
echo "Get user1's timeline"
sleep 1