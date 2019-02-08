/******************************************
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

//#ifdef __APPLE__
//#include <OpenGL/OpenGL.h>
//#include <Glut/glut.h>
//#else
#include <stdlib.h>
#include <glut.h>
//#endif
#include <assert.h>
#include <stdio.h>
#include <math.h>
#include <iostream>
#include <vector>
#include <fstream>
#include <string>
#include <iomanip>
#include <REND.h>
#include <sstream>

using namespace std;

enum mode_type{cow=1, atc,house, ball};
mode_type mode = ball;

/**********************************************************************
 * Configuration
 
 **********************************************************************/

#define INITIAL_WIDTH 800
#define INITIAL_HEIGHT 600
#define INITIAL_X_POS 200
#define INITIAL_Y_POS 200

#define WINDOW_NAME  "Lab_1 Perspective Vector Display System"

PolyModel model; //declare one object

float Xmin;
float Xmax;
float Ymin;
float Ymax;






void init(){


	if(mode == 3)
{
	Xmin = 55;
	Xmax = 200;
	Ymin = 20;
	Ymax = 200;
}
else
{
	Xmin = 0;
	Xmax = 200;
	Ymin = 0;
	Ymax = 200;
}

    glMatrixMode (GL_PROJECTION);
    //Reset the drawing perspective
    glLoadIdentity();

    gluOrtho2D(Xmin, Xmax, Ymin, Ymax);

}
void DrawGrids( void ) {
	float step = 0.1f;

	int n = 20;

	float r = step * n;

	glBegin( GL_LINES );
	
	glColor4f( 0.2f, 0.2f, 0.3f, 1.0f );

	for ( int i = -n; i <= n; i++ ) {
		glVertex3f( i * step, 0, -r );
		glVertex3f( i * step, 0, +r );
	}

	for ( int i = -n; i <= n; i++ ) {
		glVertex3f( -r, 0, i * step );
		glVertex3f( +r, 0, i * step );
	}

	glEnd();
}


void drawScene(){
	/* clear the screen and the depth buffer */
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
	// input Model file name
	string ifile;
	switch (mode){
		case 1:
		ifile = "cow.d";
		break;
		case 2:
		ifile = "atc.d";
		break;
		case 3:
		ifile = "house.d";
		break;
		case 4:
		ifile = "ball.d";
		break;

	}
    ifstream ifs(ifile.c_str());



	if(ifile=="cow.d"){
	model.setNear(10); //near
    model.setFar(200); //far
    model.setWidth(10); //h
    model.setUpVec(0,1,0);//up vector of camera
    model.setCameraPosition(3,1,-10);//set camera position on world coordinate
    model.setProjectRef(0,0,0);//set camera project reference on world coordinate
	model.setShiftLocal(8, 0,-3);//set object position on world coordinate
					}else
						if(ifile=="atc.d"){
							model.setNear(10); //near
							model.setFar(50); //far
							model.setWidth(10); //h
							model.setUpVec(0,1,0);//up vector of camera
                            model.setCameraPosition(3,1.5,-7);//set camera position on world coordinate
                            model.setProjectRef(0,0,0);//set camera project reference on world coordinate
	                        model.setShiftLocal(1, 0,-4);//set object position on world coordinate
						}else
							if(ifile=="house.d"){
								model.setNear(10); //near
								model.setFar(50); //far
								model.setWidth(10); //h
							    model.setUpVec(0,1,0);//up vector of camera
                                model.setCameraPosition(-20,0,0.1);//set camera position on world coordinate
                                model.setProjectRef(0,0,0);//set camera project reference on world coordinate
	                            model.setShiftLocal(0, 0,0);//set object position on world coordinate
							}else
								if(ifile=="ball.d"){
									model.setNear(10); //near
									model.setFar(50); //far
									model.setWidth(10); //h
									model.setUpVec(4,1,0);//up vector of camera
									model.setCameraPosition(-1,0,0);//set camera position on world coordinate
									model.setProjectRef(0,0,0);//set camera project reference on world coordinate
									model.setShiftLocal(8, 0,5);//set object position on world coordinate
								}
								

    
	


	model.setDeviceScale(Xmin, Xmax, Ymin, Ymax);
	
    model.loadModel(ifs);
  
    vector<vector<float>> temp = model.matComposite();
			
    vector< vector<int> >  front_Poly = model.m_front_poly;

    //-------------------draw function------------------
    glMatrixMode( GL_MODELVIEW );
    glLoadIdentity();

    for(int i = 0 ; i < (int)front_Poly.size() ; i++){
        for(int j = 1 ; j < front_Poly[i][0]  ; j++){
			//draw line from one vertex to the next vertex
            glBegin(GL_LINES);
                glVertex2f(temp[front_Poly[i][j]-1][0], temp[front_Poly[i][j]-1][1]);
                glVertex2f(temp[front_Poly[i][j+1]-1][0], temp[front_Poly[i][j+1]-1][1]);
            glEnd();
        }
		//connect last vertex and first vertex
        glBegin(GL_LINES);
            glVertex2f(temp[front_Poly[i][front_Poly[i][0]]-1][0], temp[front_Poly[i][front_Poly[i][0]]-1][1]);
            glVertex2f(temp[front_Poly[i][1]-1][0], temp[front_Poly[i][1]-1][1]);
        glEnd();
    }
    glutSwapBuffers();
}

int main(int argc, char** argv){
    
	glutInit (&argc, argv);   //Initialize GLUT
    glutInitDisplayMode(GLUT_RGBA | GLUT_DEPTH | GLUT_DOUBLE);
	glutInitWindowSize (INITIAL_WIDTH, INITIAL_HEIGHT);		//set windows size
    glutInitWindowPosition (INITIAL_X_POS, INITIAL_Y_POS);  //set windows position
    glutCreateWindow (WINDOW_NAME); 	//create windows

	glutDisplayFunc (drawScene);
	
	//OpenGL and other program initialization

    init();
	//Enter event processing loop
    glutMainLoop();

    return 1;
}
