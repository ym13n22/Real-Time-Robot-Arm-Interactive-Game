using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class forearmMove : MonoBehaviour
{
    private float accumulatedRotation=0f;
    private const float targetRotation=50f;
    private const float rotationSpeed=150f;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
      //  forearmRotateZ();
    }

    public  void forearmRotateZ(float rotationAngle){
        if(accumulatedRotation<targetRotation){
            float rotationThisFrame=rotationAngle;
            if(accumulatedRotation+rotationThisFrame>targetRotation){
                rotationThisFrame=targetRotation-accumulatedRotation;
            }
            accumulatedRotation +=rotationThisFrame;

            Vector3 currentRotation=transform.rotation.eulerAngles;
            currentRotation.z +=rotationThisFrame;
            transform.rotation = Quaternion.Euler(currentRotation);
            //Debug.Log("CurrentRotation is " + currentRotation);
            //Debug.Log("Time.deltaTime is " + Time.deltaTime + " rotationThisFrame is " + rotationThisFrame);
        }
    }

      public void foreArmmoveUp(float rotationAngle)
    {
        if (accumulatedRotation > 0)
        {
            float rotationThisFrame =rotationAngle;
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
    }
    public float getRotation(){
        return transform.rotation.eulerAngles.z;
    }
}
