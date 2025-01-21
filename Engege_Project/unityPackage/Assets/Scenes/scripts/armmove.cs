using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class armmove : MonoBehaviour
{
    // Start is called before the first frame update\
    private float accumulatedRotation=0f;
    private const float targetRotation=60f;

    private const float rotationSpeed=150f;

    private forearmMove forearmm;

    void Start()
    {
         forearmm = FindObjectOfType<forearmMove>();
        if (forearmm == null)
        {
            Debug.LogError("forearmMove component not found in the scene.");
            return;
        }
        
    }

    // Update is called once per frame
    void Update()
    {
      //rotateArmZ(45);
    }
    public void rotateArmZ(float rotationAngle){
    float rotateArm = 0;
    float rotateFore = 0;

    if(rotationAngle > 2000)
    {
        rotateArm = 60;
        rotateFore = rotationAngle / 60;
    }
    else if(rotationAngle > 1200 && rotationAngle <= 2000)
    {
        rotateArm = 50;
        rotateFore = rotationAngle / 50;
    }
    else if(rotationAngle > 600 && rotationAngle <= 1200)
    {
        rotateArm = 40;
        rotateFore = rotationAngle / 40;
    }
    else if(rotationAngle > 400 && rotationAngle <= 600)
    {
        rotateArm = 30;
        rotateFore = rotationAngle / 30;
    }
    else if(rotationAngle > 200 && rotationAngle <= 400)
    {
        rotateArm = 15;
        rotateFore = rotationAngle / 15;
    }
    else if(rotationAngle > 100 && rotationAngle <= 200)
    {
        rotateArm = 0;
        rotateFore = rotationAngle / 20;
    }
    else if(rotationAngle > 50 && rotationAngle <= 100)
    {
        rotateArm = 0;
        rotateFore = 0;
    }
    else if(rotationAngle > 0 && rotationAngle <= 50)
    {
        rotateArm = 0;
        rotateFore = 0;
    }



        
        if(accumulatedRotation<targetRotation){
           
            float rotationThisFrame=rotateArm;
           // Debug.Log("rotateArmZ method called");
            if(accumulatedRotation+rotationThisFrame>targetRotation){
                rotationThisFrame=targetRotation-accumulatedRotation;
            }
            accumulatedRotation+=rotationThisFrame;
            Vector3 currentRotation = transform.rotation.eulerAngles;
            currentRotation.z +=rotationThisFrame;
            transform.rotation=Quaternion.Euler(currentRotation);

           // Debug.Log("CurrentRotation is " + currentRotation);
           // Debug.Log("Time.deltaTime is " + Time.deltaTime + " rotationThisFrame is " + rotationThisFrame);
        }
        forearmm.forearmRotateZ(rotateFore);
    }

    public void rotateArmZOnce(){
        
        
        if(accumulatedRotation<targetRotation){
           
            float rotationThisFrame=rotationSpeed * Time.deltaTime;
            //Debug.Log("rotateArmZ method called");
            if(accumulatedRotation+rotationThisFrame>targetRotation){
                rotationThisFrame=targetRotation-accumulatedRotation;
            }
            accumulatedRotation+=rotationThisFrame;
            Vector3 currentRotation = transform.rotation.eulerAngles;
            currentRotation.z +=rotationThisFrame;
            transform.rotation=Quaternion.Euler(currentRotation);

            //Debug.Log("CurrentRotation is " + currentRotation);
            //Debug.Log("Time.deltaTime is " + Time.deltaTime + " rotationThisFrame is " + rotationThisFrame);
        }
        forearmm.forearmRotateZ(45);
    }




    public void armmoveUp(float rotationAngle)
    {

        float rotateArm = 0;
        float rotateFore = 0;

        if(rotationAngle > 2000)
        {
            rotateArm = 60;
            rotateFore = rotationAngle / 60;
        }
        else if(rotationAngle > 1200 && rotationAngle <= 2000)
        {
            rotateArm = 50;
            rotateFore = rotationAngle / 50;
        }
        else if(rotationAngle > 600 && rotationAngle <= 1200)
        {
            rotateArm = 40;
            rotateFore = rotationAngle / 40;
        }
        else if(rotationAngle > 400 && rotationAngle <= 600)
        {
            rotateArm = 30;
            rotateFore = rotationAngle / 30;
        }
        else if(rotationAngle > 200 && rotationAngle <= 400)
        {
            rotateArm = 15;
            rotateFore = rotationAngle / 15;
        }
        else if(rotationAngle > 100 && rotationAngle <= 200)
        {
            rotateArm = 10;
            rotateFore = rotationAngle / 10;
        }
        else if(rotationAngle > 80 && rotationAngle <= 100)
        {
            rotateArm = 3;
            rotateFore = rotationAngle / 3;
        }
        else if(rotationAngle > 0 && rotationAngle <= 80)
        {
            rotateArm = 0;
            rotateFore = 0;
        }



        if (accumulatedRotation > 0)
        {
            float rotationThisFrame =rotateArm ;
            if (accumulatedRotation - rotationThisFrame < 0)
            {
                rotationThisFrame = accumulatedRotation;
            }
            accumulatedRotation -= rotationThisFrame;
            Vector3 currentRotation = transform.rotation.eulerAngles;
            currentRotation.z -= rotationThisFrame;
            transform.rotation = Quaternion.Euler(currentRotation);

            //Debug.Log("armmoveUp method called");
            //Debug.Log("CurrentRotation is " + currentRotation);
            //Debug.Log("Time.deltaTime is " + Time.deltaTime + " rotationThisFrame is " + rotationThisFrame);
        }
        forearmm.foreArmmoveUp(rotateFore);
    }
    public float getRotation(){
        return transform.rotation.eulerAngles.z;
    }
}
