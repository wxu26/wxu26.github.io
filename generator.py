import os
from PIL import Image,ImageOps

i_cut = 30 # seperate header and footer of ph

# read list of photos & store small images
images = []
for file in os.listdir("./photos_img/"):
    if file.endswith(".jpeg") or file.endswith(".jpg"):
    	images.insert(0,file)
images.sort()
images = images[::-1]
print(images)
N = len(images)
for img in images:
	img_small=Image.open("./photos_img/"+img)
	img_small=ImageOps.fit(img_small, (500,500), Image.ANTIALIAS)
	img_small.save('./photos_img_small/'+img)

# write photo.html
with open('photo_template.html','r') as f:
	head = f.readlines()
with open('photo_template_footer.html','r') as f:
	foot = f.readlines()
with open('photo.html','w') as f:
	f.writelines(head)
	for n in range(N):
		one_img = '<a href="photos/'+str(n)+'.html"><img src="./photos_img_small/'+images[n]+'"><div class="pointer" id="'+str(n)+'"></div><div class="zoom"></div></a>\n'
		f.write(one_img)
	f.writelines(foot)

# write individual pages
with open('./photos/single_photo_template.html','r') as f:
	data=f.readlines()
	top = data[:10]
	mid = data[11:14]
	bot = data[15:]
for n in range(N):
	with open('./photos/'+str(n)+'.html','w') as f:
		f.writelines(top)
		if n==0:
			f.write('<a href="../photo.html#1" class="prev">PREV</a>\n')
		else:
			f.write('<a href="../photos/'+str(n-1)+'.html" class="prev">PREV</a>\n')
		f.write('<a href="../photo.html#'+str(n)+'">BACK</a>\n')
		if n==N-1:
			f.write('<a href="../photo.html#'+str(N-1)+'" class="next">NEXT</a>\n')
		else:
			f.write('<a href="../photos/'+str(n+1)+'.html" class="next">NEXT</a>\n')
		f.writelines(mid)
		f.write('<img src="../photos_img/'+images[n]+'">')
		f.writelines(bot)

