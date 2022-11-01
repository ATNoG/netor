# # @Author: Daniel Gomes
# # @Date:   2022-11-01 15:51:56
# # @Email:  dagomes@av.it.pt
# # @Copyright: Insituto de Telecomunicações - Aveiro, Aveiro, Portugal
# # @Last Modified by:   Daniel Gomes
# # @Last Modified time: 2022-11-01 16:29:31


# # general imports
# import pytest

# # custom imports
# from schemas import domain as DomainSchemas
# from sql_app.crud import domain as CRUDDomain
# from configure_test_idp import (
#     setup_test_idp,
# )


# def import_modules():
#     # additional custom imports
#     from configure_test_db import (
#         engine as imported_engine,
#         test_client as imported_test_client,
#         override_get_db as imported_override_get_db
#     )
#     from sql_app.database import Base as imported_base
#     global engine
#     engine = imported_engine
#     global Base
#     Base = imported_base
#     global test_client
#     test_client = imported_test_client
#     global override_get_db
#     override_get_db = imported_override_get_db


# def create_domain(database):
#     ownedLayer = DomainSchemas.OwnedLayersCreate(
#         domainLayerId="ITAV_OSM",
#         domainLayerType="OSM_NSP",
#         username="5gasp",
#         password="blallalsad",
#         project="5gasp",
#         vimAccount="Tron"
#     )
#     domain = DomainSchemas.DomainCreate(
#         domainId="ITAv",
#         name="ITAv domain",
#         description="ITAv domain description",
#         url="http://10.0.10.10",
#         interfaceType="HTTP",
#         ownedLayers=[ownedLayer],
#         auth=False,
#         admin="ITAv",
#         owner="admin"
#     )

#     result = CRUDDomain.createDomain(
#         db=database,
#         domain_data=domain
#     )
#     return result

# # Create the DB before each test and delete it afterwards
# @pytest.fixture(autouse=True)
# def setup(monkeypatch, mocker):
#     # Setup Test IDP.
#     # This is required before loading the other modules
#     setup_test_idp(monkeypatch, mocker)
#     import_modules()
#     Base.metadata.create_all(bind=engine)
#     yield
#     Base.metadata.drop_all(bind=engine)


# def test_complex_domain_database_update():
#     database = next(override_get_db())
#     db_domain = create_domain(database)
#     ownedLayer = DomainSchemas.OwnedLayersCreate(
#         domainLayerId="ITAV_OSM",
#         domainLayerType="OSM_NSP",
#         username="5gasp",
#         password="new_password",
#         project="5gasp",
#         vimAccount="New VIM"
#     )
#     domain = DomainSchemas.DomainUpdate(
#         domainId="ITAv",
#         name="ITAv domain new name",
#         description="ITAv domain new description",
#         url="http://10.0.10.11",
#         interfaceType="HTTP",
#         ownedLayers=[ownedLayer],
#         auth=False,
#         admin="ITAv",
#         owner="admin"
#     )
#     updated_domain = CRUDDomain.updateDomain(
#         database,
#         db_domain,
#         domain)
#     updated_layer = updated_domain['ownedLayers'][0]
#     print(updated_domain['ownedLayers'])
#     assert updated_domain['name'] == domain.name
#     assert updated_domain['description'] == domain.description
#     assert updated_domain['url'] == domain.url
    
#     assert updated_layer['vimAccount'] == ownedLayer.vimAccount
#     #assert updated_layer['password'] == ownedLayer.password
