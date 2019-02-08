/******************************************
Lab 1 Perspective Vector Display System


THE GEORGE WASHINGTON UNIVERSITY 
Department of Computer Science 
CS 6554 - Computer Graphics II - Spring 2014 
 
Assignment 1 Due: 2/6 
Perspective Vector Display System 
 
 
Description: You are to implement a system to read in a geometric data of a polygonal object 
and to display the object using perspective transformation. You need not write the clipping 
routine (assume that the object will always be in the viewing volume) unless you have already 
done this lab before (in which case, you should extend it to include clipping). 
 
Input: a) Geometric data for a polygonal object (Some example files are in 
http://www.icg.gwu.edu/cs266/resources/model_osu/model_osu.html). A good 
example is the house. The file format you should use is the “.d” file format 
described below. 
 b) Viewing specification 
 
Output: Perspective view of the object displayed on the viewport with back faces 
removed. 
 
Email: Source code. It is important that the grader understand your code. Put enough 
comments to make it clear what you are doing. 
 
Put on the class web page (http://www.icg.seas.gwu.edu/academicPrograms_cs263.htm): 
a) Some images generated with your code. 
b) A short description of your system 
Put on Blackboard 
a) The source code 
 
Data format: 
a) the word "data" followed by the number of points and the number of polygons 
b) points given by: the x, y, z coordinates 
c) polygons given by: number of points in the polygon followed by vertex number in 
clockwise order (when looking from outside the object) 
******************************************/

#ifndef POLYMODEL_H
#define POLYMODEL_H

#pragma once
#include "stdafx.h"
#include <string>
#include <vector>
#include <iostream>

using namespace std;

class PolyModel{
    public:
		//vectors for original vertex coordinates and polygons
        vector< vector<float> > m_verts;
        vector< vector<int> > m_polys;

		//vector for visible face polygons and corresponding indexes
        vector<int>  m_front_index;     
        vector< vector<int> > m_front_poly;
		
		//constructor
		PolyModel(){};

		//load data from ".d" file
        bool loadModel(istream& istr, bool reverse=false);
        
		//compute back face and normalized vertices data
        vector< vector<float> > matComposite();
        
        virtual ~PolyModel();

		//set vector for object shift from local to world
        void setShiftLocal(float, float, float);
		//set Camera position in world coordinate
        void setCameraPosition(float, float, float);
        //set up vector for camera
        void setUpVec(float, float, float);
        //set near clipping distance
        void setNear(float);
        //set far clipping distance
        void setFar(float);
        //set h for perspective matrix
        void setWidth(float);
		//set scale to device coordinate Xmin, Ymin, Xmax, Ymax
		void setDeviceScale(float, float, float, float);
        //set project reference for camera
        void setProjectRef(float, float, float);
		
		//compute N vector for camera
        void view_N(vector<float> &, vector<float>, vector<float>);
		//compute U vector for camera
        void view_U(vector<float> &, vector<float>, vector<float>);
		//compute V vector for camera
        void view_V(vector<float> &, vector<float>, vector<float>);

		//compute vector length
		float vector_length(vector<float>);
        //compute vector subtraction
        void vector_subtraction(vector<float> &, vector<float>, vector<float>);

        //compute dot product
        float dot_product(vector<float> , vector<float> );
        //compute cross product
        void cross_product(vector<float> &, vector<float>, vector<float>);

		// compute the multiplication of two matrices
        void matrix4x1(vector <float> &, vector< vector<float> >,vector <float>);
        // compute the multiplication of two 4x4 matrices
        void matrix4x4(vector< vector<float> >&, vector< vector<float> >,vector< vector<float> >);
		
        //compute modeling transformation matrix
        void matrixModel(vector< vector<float> >&, vector<float>);
        //compute viewing transformation Matrix
        void matrixView(vector< vector<float> >& , vector<float> , vector<float>);
        //compute projection transformation matrix
        void matrixPers(vector< vector<float> >&  , float , float , float );

    private:
        char *fileName;

        vector <float> localToWorld;
        vector <float> camera; //camera position in world
        vector <float> up_vector;//up vector for camera
        vector<float> P_ref;//project reference for camera

        float h;//for perspective matrix
		float near;//near clipping plan
        float far;//far clipping plan
		float Near;//near clipping plan
        float Far;//far clipping plan
		float Xmin;
        float Ymin;
        float Xmax;
        float Ymax;

        vector< vector<float> > m_model;//Modeling transform Matrix
		vector< vector<float> > m_view;//view transformation Matrix
        vector< vector<float> > m_pers;//Perspective transform Matrix
        
    protected:

};

#endif // POLYMODEL_H
