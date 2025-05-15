using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class AAAA : MonoBehaviour
{

    [SerializeField] GameObject ocultar;
    [SerializeField] GameObject mostrar;
    // Start is called before the first frame update
    public void cambio()
    {

        ocultar.SetActive(false);
        mostrar.SetActive(true);

    }
}
