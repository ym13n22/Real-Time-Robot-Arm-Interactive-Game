using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class handMove : MonoBehaviour
{
    private float accumulatedRotation=0f;
    private const float targetRotation=50;

    private const float rotationSpeed=100f;
    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
      //  rotateHandZ();
    }
    private void rotateHandZ(){
        if(accumulatedRotation<targetRotation){
            float rotationThisFrame = rotationSpeed*Time.deltaTime;
            if(accumulatedRotation+rotationThisFrame > targetRotation){
                rotationThisFrame = targetRotation-accumulatedRotation;
            }
            accumulatedRotation +=rotationThisFrame;
            Vector3 currentRotation = transform.rotation.eulerAngles;
            currentRotation.z += rotationThisFrame;
            transform.rotation = Quaternion.Euler(currentRotation);
            //Debug.Log("CurrentRotation is " + currentRotation);
            //Debug.Log("Time.deltaTime is " + Time.deltaTime + " rotationThisFrame is " + rotationThisFrame);
        }
    }
}
