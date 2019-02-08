/******************************************
Lab 1 Perspective Vector Display System

THE GEORGE WASHINGTON UNIVERSITY 
Department of Computer Science 
CS 6554 - Computer Graphics II - Spring 2014 

Name: Wenhui Zhang	
GWid: G35379915
 
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

#include "stdafx.h"
#include "PolyModel.h"

/*
#ifdef __APPLE__
#include <OpenGL/OpenGL.h>
#include <Glut/glut.h>
#else  */
#include <GL/glut.h>
// #endif
#include <vector>
#include <iostream>
#include <fstream>
#include <string>
#include <cstring>
#include <cstdlib>
#include <math.h>
#include <iomanip>

using namespace std;

enum backface_culling{no=1, yes=2};
backface_culling mode = yes;


bool PolyModel::loadModel(std::istream& istr, bool reverse){
    //load filename *.d
    if (!istr.good())
		return false;

	//declare two variables to store the number of vertex and polygon
    int vertex_count, face_count;

    //store first word "data"
    string data;

    char firstline[50];
    istr.getline(firstline, 50, '\n');
    istr.seekg(0L, ios::beg);
    string string = firstline; 

    if(!string.find("data")){
		//first line include word "data"
        istr >> data >> vertex_count >> face_count;
    }
    else{
		//first line doesn't include word "data"
        istr >> vertex_count >> face_count;
    }
	//declare a vector to store vertice coordinates
    vector<float>vertex(4);
    
    // Read in all the points, assign vertex to public vector vec_vertex
    for(int i = 0; i< vertex_count; i++){
        istr >> vertex[0] >> vertex[1] >> vertex[2];
        vertex[3] = 1;
		m_verts.push_back(vertex);
    } 

    // Read in all the polygons
    for(int i = 0; i< face_count; i++){
        int element,index;
		//read in vertex index
        istr>>index;
		//declare a vector to store all the points of each polygon
        vector<int> poly;
		//store index of each polygon into row vector
        poly.push_back(index);

		//read in all the points of each polygon
        for (int j = 0; j < index; j++){
            istr>>element;
            poly.push_back(element); 
        }
		// assign the vector to the public vector vec_polygon
        m_polys.push_back(poly);
    }
    return true;
}

vector< vector<float> > PolyModel::matComposite(){
	//initialize modeling, viewing, perspective transformation vectors
	vector< vector<float> > m_model(4, vector<float>(4));
	vector< vector<float> > m_view (4, vector<float>(4));
	vector< vector<float> > m_pers (4, vector<float>(4));

	//compute Modeling transform Matrix
    matrixModel(m_model, localToWorld);
    //compute viewing transform Matrix
    matrixView(m_view , camera, up_vector);
    //compute Perspective transform Matrix
    matrixPers(m_pers ,Near,  Far,  h);
    
    vector< vector<float> > m_model_view(4, vector<float> (4));
	//compute composite matrix to view space
    matrix4x4(m_model_view, m_view, m_model);
    
	//vec_view_vertex stores vertices in view space
    vector< vector<float> > temp_vertex(m_verts.size(), vector<float>(4));
    
    for(int i = 0 ; i < (int)m_verts.size() ; i++)
	  //vertice in view space
      matrix4x1(temp_vertex[i] , m_model_view, m_verts[i]);
        
    //start front face calculus in view space
    vector <float> view_normal(3);
    vector <float> poly_vector_1(3);
    vector <float> poly_vector_2(3);
    vector <float> poly_normal(3);
    vector <float> front_vertex;//store all 'front vertices' index























    
	//compute faces
    for(int i=0; i<(int)m_polys.size(); i++){
		//compute two vectors on one polygon
        vector_subtraction(poly_vector_1, temp_vertex[m_polys[i][2]-1], temp_vertex[m_polys[i][1]-1]);
        vector_subtraction(poly_vector_2, temp_vertex[m_polys[i][2]-1], temp_vertex[m_polys[i][3]-1]);
        //compute the direction to the camera
        vector_subtraction(view_normal, camera, temp_vertex[m_polys[i][2]-1]);
        //calculus cross product
        cross_product(poly_normal, poly_vector_1, poly_vector_2);
	
	/*back face culling or not*/
	switch (mode){

	case 1: {
		//compute all faces, before back face culling
		  
        if(dot_product(poly_normal,view_normal)){
           //store front 'polygon index'
		   m_front_index.push_back(i);
		   for(int j=1; j< (int)m_polys[i][0]+1; j++)
                front_vertex.push_back(m_polys[i][j]);
		      
		} }
			break;
	case 2: {

	
		//compute visible face, after back face culling

        //detect visible face if dot product greater than 0
        if(dot_product(poly_normal,view_normal)>0){
           //store front 'polygon index'
		   m_front_index.push_back(i);
            
           for(int j=1; j< (int)m_polys[i][0]+1; j++)
                front_vertex.push_back(m_polys[i][j]);

		     
        }} 
			break;
	}

		
    }


	

    for(int i=0; i< (int)m_front_index.size(); i++)
	  //store front face polygon data
      m_front_poly.push_back(m_polys[m_front_index[i]]);
      
	  //mark visible vertices by add extra number at the back of them
      for(int i = 0 ; i < (int)front_vertex.size() ; i++){
        if(temp_vertex[front_vertex[i]-1].size() == 4){
			vector<float>temp(4);
			//compute vertices in perspective space from view space vertices
			matrix4x1(temp, m_pers, temp_vertex[front_vertex[i]-1]);
			for(int j = 0; j < 4; j++){
			//compute nomalized vertices through divide by W
				temp[j] /= temp[3];
			}
			temp[0] = ((Xmax - Xmin)/2)*(temp[0]+1);
			temp[1] = ((Ymax - Ymin)/2)*(temp[1]+1);
			temp_vertex[front_vertex[i]-1] = temp;
            temp_vertex[front_vertex[i]-1].push_back(-1);
		}
    }
	return temp_vertex;
}

void PolyModel::setShiftLocal(float x, float y, float z){
	//set vector that object shift from local to world
    localToWorld.push_back(x);
    localToWorld.push_back(y);
    localToWorld.push_back(z);
}

void PolyModel::setCameraPosition(float x, float y, float z){
	//set Camera position in world coordinate
    camera.push_back(x);
    camera.push_back(y);
    camera.push_back(z);
}

void PolyModel::setUpVec(float x, float y, float z){
	//set up vector for camera
    up_vector.push_back(x);
    up_vector.push_back(y);
    up_vector.push_back(z);
}

void PolyModel::setNear(float Near){
	//set near clipping plan =>near
  near= Near;

}


void PolyModel::setFar(float Far){
	//set far clipping plan => far
   far=Far;
}


void PolyModel::setWidth(float width){
	//set h for perspective matrix
    h = width;
}


void PolyModel::setDeviceScale(float x, float X,float y, float Y){
    Xmin = x;
    Xmax = X;
    Ymin = y;
    Ymax = Y;
}

void PolyModel::setProjectRef(float x, float y, float z){
	//set project reference for camera
    P_ref.push_back(x);
    P_ref.push_back(y);
    P_ref.push_back(z);
}

void PolyModel::view_N(vector<float> &N_vector, vector<float> camera, vector<float> vertex){
	//compute N vector for viewpoint
    vector<float> num(3); //P.ref - C
    float den; //|P.ref - C|
	//vertex[3] => P_reference, camera[3] => camera position at World coordinate
    vector_subtraction(num, camera, vertex); 
    den = vector_length(num); //|P.ref - C|
    for(int i = 0 ; i < 3 ; i++)
        N_vector[i] = num[i]/den;
}

void PolyModel::view_U(vector<float> &U_vector,vector<float> N_vector , vector<float> up_vector){
	//compute U vector for camera
    vector<float> num(3); // N x V'
    float den; //|N x V'|
    cross_product(num , N_vector, up_vector); // N x V'
    den = vector_length(num); // |N x V'|

    for(int i = 0 ; i < 3 ; i++)
        U_vector[i] = num[i]/den;
}

void PolyModel::view_V(vector<float> &V_vector,vector<float> U_vector, vector<float> N_vector){
	//compute V vector for camera
    //V = U x N
	for(int i = 0 ; i < 3 ; i++)
        U_vector[i] = U_vector[i];
    cross_product(V_vector , U_vector , N_vector);
	
}

float PolyModel::vector_length(vector<float> vector_1){
	//compute vector length
    return sqrt(vector_1[0]*vector_1[0] + vector_1[1]*vector_1[1] + vector_1[2]*vector_1[2]);
}

void PolyModel::vector_subtraction(vector<float> &sub,vector<float> vector_1, vector<float> vector_2){
	//compute vector subtraction
    //vector_2 - vector_1
    for(int i = 0 ; i < 3 ; i++)
        sub[i] = vector_2[i] - vector_1[i];
}

float PolyModel::dot_product(vector<float> vector_1,vector<float> vector_2){
	//compute dot product
    return vector_1[0]*vector_2[0] + vector_1[1]*vector_2[1] + vector_1[2]*vector_2[2];
}

void PolyModel::cross_product(vector<float> &normal,vector<float>vector_1, vector<float>vector_2){
	//compute cross product
    normal[0] = vector_1[1]*vector_2[2] - vector_2[1]*vector_1[2];
    normal[1] = -(vector_1[0]*vector_2[2] - vector_2[0]*vector_1[2]);
    normal[2] = vector_1[0]*vector_2[1] - vector_2[0]*vector_1[1];
}

void PolyModel::matrix4x1(vector <float> &matrix_out,vector< vector<float> >matrix_L,vector <float>matrix_R){
	// compute 4 x 4 and 4 x 1 matrices muliplication
    for(int i = 0 ; i < 4 ; i++ ){
        matrix_out[i] =
            matrix_L[i][0] * matrix_R[0] +
            matrix_L[i][1] * matrix_R[1] +
            matrix_L[i][2] * matrix_R[2] +
            matrix_L[i][3] * matrix_R[3] ;
    }
}

void PolyModel::matrix4x4(vector< vector<float> > &matrix_out,vector< vector<float> >matrix_L,vector< vector<float> >matrix_R){
	// compute 2 4 x 4 matrices muliplication
    for(int i = 0 ; i < 4 ; i++ )
        for(int j = 0 ; j < 4 ; j++ ){
            matrix_out[i][j] =
                matrix_L[i][0] * matrix_R[0][j] +
                matrix_L[i][1] * matrix_R[1][j] +
                matrix_L[i][2] * matrix_R[2][j] +
                matrix_L[i][3] * matrix_R[3][j];
        }
}

void PolyModel::matrixModel(vector< vector<float> >& m_model, vector<float> toWorld){
	//compute modeling matrix
    //m_model => Modeling Matrix
    //offset => vector from local to world
    for(int i = 0 ; i < 4 ; i++)
        for(int j = 0 ; j < 4 ; j++ ){
            if(i == j)
                m_model[i][j] = 1;
            else if(i == 0 && j ==3 )
                m_model[i][j] = toWorld[0];
            else if(i == 1 && j ==3 )
                m_model[i][j] = toWorld[1];
            else if(i == 2 && j ==3 )
                m_model[i][j] = toWorld[2];
            else
                m_model[i][j] = 0;
        }
}

void PolyModel::matrixView(vector< vector<float> >& m_view,vector<float> camera, vector<float> up_vector){
	//compute view transformation Matrix
	//rotate matrix
    vector< vector<float> > m_viewR(4, vector<float>(4));
    //translate matrix
    vector< vector<float> > m_viewT(4, vector<float>(4));
    
    for(int i=0; i<4; i++)
        for(int j=0; j<4; j++){
            if(i == j){
                m_viewR[i][j] = 1;
                m_viewT[i][j] = 1;
            }
            else{
                m_viewR[i][j] = 0;
                m_viewT[i][j] = 0;
            }
        }

    for(int i=0; i<3; i++)
        m_viewT[i][3] = -camera[i];

    //    m_viewR[2] => Nx Ny Nz
    view_N(m_viewR[2], camera , P_ref);
    //    m_viewR[0] => Ux Uy Uz
    view_U(m_viewR[0], m_viewR[2], up_vector);
    //    m_viewR[1] => Vx Vy Vz
    view_V(m_viewR[1], m_viewR[0], m_viewR[2]);

    matrix4x4(m_view, m_viewR , m_viewT);
}

void PolyModel::matrixPers(vector< vector<float> >& m_pers, float d, float f, float h){
	//compute perspective matrix
    for(int i=0; i<4; i++)
        for(int j=0; j<4; j++){
            if(i == 0 && j ==0)
                m_pers[i][j] = 0.5;
            else if(i == 1 && j ==1)
                m_pers[i][j] = float(0.65);
            else if (i == 2 && j ==2)
                m_pers[i][j] = f / (f - d);
            else if (i == 2 && j ==3)
                m_pers[i][j] = - f * d / (f - d);
            else if (i == 3 && j ==2)
                m_pers[i][j] = 1;
            else
                m_pers[i][j] = 0;
        }
}

PolyModel::~PolyModel()
{
}
