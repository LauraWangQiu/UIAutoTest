using System.Collections.Generic;
using UnityEngine;
using TMPro;

public class GoToComponent : MonoBehaviour
{
	private TMP_InputField inputField;

	[SerializeField] List<GameObject> objetos;

	private void Start()
	{
		inputField = GetComponent<TMP_InputField>();
	}
	public void ActivarObjetoPorNombre()
	{
		string nombre = inputField.text.Trim();
		foreach (GameObject go in objetos)
		{
			if (go.name == nombre)
			{
				go.SetActive(true);
				this.gameObject.SetActive(false);
				return;
			}
		}
	}
}