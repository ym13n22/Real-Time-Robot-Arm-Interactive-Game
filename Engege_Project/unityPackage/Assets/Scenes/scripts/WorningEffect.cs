using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class worningEffects : MonoBehaviour
{
    // Start is called before the first frame update
    private squre1 sq1;
    private squre2 sq2;

    private squre3 sq3;
    void Start()
    {
        sq1=FindObjectOfType<squre1>();
        sq2=FindObjectOfType<squre2>();
        sq3=FindObjectOfType<squre3>();
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    public void worningEffect(){
        if(sq1!=null){
        sq1.startEffect();
        sq2.startEffect();
        sq3.startEffect();
        }
        
    }
}
