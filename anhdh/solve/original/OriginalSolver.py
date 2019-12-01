#!/usr/bin/env python
# -*- coding: utf-8 -*-

from anhdh.Common import Common
import cv2
from PIL import Image
import glob
import numpy as np
import os
import math

class OriginalSolver(Common):
    def __init__(self, img_path):
        Common.__init__(self, img_path)
        self.FLANN_INDEX_KDTREE = 0
        self.MIN_MATCH_COUNT = 10
        self.descriptor = cv2.xfeatures2d.SIFT_create()
        self.listsubimg_path = glob.glob(f"{self.raster_folder}/*.png")
        # self.image = Image.open(img_path).convert('RGB') # L is Gray
        self.image = cv2.imread(img_path)
        self.listsubimage = [cv2.imread(path) for path in self.listsubimg_path]
        self.init_size()

    def init_size(self):
        self.width, self.height = self.image.shape[:2]
        self.num_horizontal  = math.ceil(self.height/self.listsubimage[0].shape[0]) # ngang
        self.num_vertical  = math.ceil(self.width/self.listsubimage[0].shape[1]) # doc
        print(self.num_horizontal, self.num_vertical)

    def detectAndDescribe(self, image):
        # convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        (kps, features) = self.descriptor.detectAndCompute(image, None)
        # convert the keypoints from KeyPoint objects to NumPy arrays
        kps = np.float32([kp.pt for kp in kps])
        # return a tuple of keypoints and features
        return (kps, features)
    
    def matchKeypoints(self, kpsA, kpsB, featuresA, featuresB, ratio, reprojThresh):
        # compute the raw matches and initialize the list of actual
        # matches
        matcher = cv2.DescriptorMatcher_create("BruteForce")
        rawMatches = matcher.knnMatch(featuresA, featuresB, 2)
        matches = []

        # loop over the raw matches
        for m in rawMatches:
            # ensure the distance is within a certain ratio of each
            # other (i.e. Lowe's ratio test)
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                matches.append((m[0].trainIdx, m[0].queryIdx))

        # computing a homography requires at least 4 matches
        if len(matches) > 4:
            # construct the two sets of points
            ptsA = np.float32([kpsA[i] for (_, i) in matches])
            ptsB = np.float32([kpsB[i] for (i, _) in matches])

            # compute the homography between the two sets of points
            (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC,
                reprojThresh)

            # return the matches along with the homograpy matrix
            # and status of each matched point
            return (matches, H, status)

        # otherwise, no homograpy could be computed
        return None
    def drawMatches(self, imageA, imageB, kpsA, kpsB, matches, status):
        # initialize the output visualization image
        (hA, wA) = imageA.shape[:2]
        (hB, wB) = imageB.shape[:2]
        vis = np.zeros((max(hA, hB), wA + wB, 3), dtype="uint8")
        vis[0:hA, 0:wA] = imageA
        vis[0:hB, wA:] = imageB

        checker =  (status == 1)
        if len(checker[checker ==  True]) == 0:
            return None
        # loop over the matches
        for ((trainIdx, queryIdx), s) in zip(matches, status):
            # only process the match if the keypoint was successfully
            # matched
            if s == 1:
                # draw the match
                ptA = (int(kpsA[queryIdx][0]), int(kpsA[queryIdx][1]))
                ptB = (int(kpsB[trainIdx][0]) + wA, int(kpsB[trainIdx][1]))
                cv2.line(vis, ptA, ptB, (0, 255, 0), 1)

        # return the visualization
        return vis

    def solve(self):
        # self.kps, self.des = self.detectAndDescribe(self.image)
        # self.list_kp_des2 = [self.detectAndDescribe(image) for image in self.listsubimage]


        # for i in range(len(self.listsubimage)):
        #     M = self.matchKeypoints(self.kps, self.list_kp_des2[i][0], self.des, self.list_kp_des2[i][1], 0.75, 5.0)
        #     if M is not None:
        #         (matches, H, status) = M
        #         vis = self.drawMatches(self.image, self.listsubimage[i], self.kps, self.list_kp_des2[i][0], matches, status)
        #         if  vis is not None:
        #             path = os.path.join(self.matches_folder, f"{i}.png")
        #             cv2.imwrite(path, vis)
        #             abc = ""

        self.kps, self.des = self.descriptor.detectAndCompute(self.image, None)
        self.list_kp_des = [self.descriptor.detectAndCompute(image, None) for image in self.listsubimage]

        flann = self.create_flann(self.FLANN_INDEX_KDTREE)

        self.matches = [flann.knnMatch(self.des,sub_des,k=2) for sub_kps, sub_des in self.list_kp_des]
        self.match_imgs = [self.get_match_img(match, idx, 0.75, self.MIN_MATCH_COUNT) for (idx, match) in enumerate(self.matches) ]
        for idx, img in enumerate(self.match_imgs):
            cv2.imwrite(os.path.join(self.matches_folder, f"{idx}.png"), img)

    def create_flann(self, flann_index_kdtree, trees = 5, checks = 50):
        index_params = dict(algorithm = flann_index_kdtree, trees = trees)
        search_params = dict(checks=checks)
        flann = cv2.FlannBasedMatcher(index_params,search_params)
        return flann

    def get_match_img(self, match, idx, ratio = 0.75, min_match = 10, randsac_ratio  = 5.0):
        matchesMask = [[0,0] for i in range(len(match))]
        good = []
        for i,(m,n) in enumerate(match):
            if m.distance < ratio*n.distance:
                good.append(m)
                matchesMask[i]=[1,0]
                
        print("Number of matchesMask: " + str(len(good)))
        sub_kps, sub_des = self.list_kp_des[idx]
        if len(good)>min_match:
            src_pts = np.float32([ self.kps[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
            dst_pts = np.float32([ sub_kps[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, randsac_ratio)
            if M is not None:
                matchesMask = mask.ravel().tolist()

                d,h,w = self.image.shape[::-1]
                pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
                dst = cv2.perspectiveTransform(pts,M)

                self.listsubimage[idx] = cv2.polylines(self.listsubimage[idx],[np.int32(dst)],True,255,3, cv2.LINE_AA)

        else:
            print("Not enough matches are found - %d/%d" % (len(good),min_match))
            matchesMask = None

        draw_params = dict(matchColor = (0,255,0),
                        singlePointColor = None,
                        matchesMask = matchesMask,
                        flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        
        imgRes = cv2.drawMatches(self.image, self.kps, self.listsubimage[idx], sub_kps,good,None,**draw_params)
        # imgRes = cv2.drawMatchesKnn(self.image, self.kps, self.listsubimage[idx], sub_kps, self.matches[idx], None,**draw_params)
        return imgRes

        